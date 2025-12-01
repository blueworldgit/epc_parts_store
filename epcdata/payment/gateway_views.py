"""
Gateway API views for Worldpay direct payment processing
"""
import logging
from decimal import Decimal
from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import View, TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.clickjacking import xframe_options_exempt
from django.utils.decorators import method_decorator
from oscar.apps.checkout.session import CheckoutSessionMixin
from oscar.core.loading import get_model, get_class
from oscar.apps.order.utils import OrderCreator

from .gateway_facade import WorldpayGatewayFacade
from .card_forms import WorldpayCardDetailsForm

logger = logging.getLogger(__name__)

Order = get_model('order', 'Order')
OrderPlacementMixin = get_class('checkout.mixins', 'OrderPlacementMixin')


class WorldpayGatewayRedirectView(OrderPlacementMixin, CheckoutSessionMixin, View):
    """
    View to redirect to Worldpay Gateway card details form
    """
    
    def get(self, request, *args, **kwargs):
        """
        Redirect to card details collection form
        """
        # Check pre-conditions for checkout
        try:
            submission = self.build_submission()
            logger.info(f"Built submission successfully for Gateway API")
            logger.info(f"Order total: {submission['order_total']}")
        except Exception as e:
            logger.warning(f"Checkout submission failed: {str(e)}")
            messages.error(request, _("Your checkout session has expired. Please start again."))
            return HttpResponseRedirect(reverse('checkout:index'))
        
        # Check if payment is required
        if not submission['order_total'].incl_tax:
            logger.info("No payment required for this order")
            messages.info(request, _("No payment is required for this order."))
            return HttpResponseRedirect(reverse('checkout:preview'))
        
        # Store submission in session for card details form
        try:
            # Generate a unique order number for this payment session
            from oscar.apps.order.utils import OrderNumberGenerator
            import time
            from decimal import Decimal, ROUND_HALF_UP
            generator = OrderNumberGenerator()
            base_order_number = generator.order_number(submission['basket'])
            
            # Add timestamp to ensure uniqueness in case of retries
            timestamp = int(time.time() % 10000)  # Last 4 digits of timestamp
            order_number = f"{base_order_number}-{timestamp}"
            
            logger.info(f"🎯 Generated unique order number: {order_number}")
            logger.info(f"📦 Basket details: ID={submission['basket'].id}, items={submission['basket'].num_items}, total={submission['basket'].total_incl_tax}")
            
            # Calculate UK VAT (20%) on combined product + shipping total
            products_total = Decimal(str(submission['basket'].total_incl_tax))
            shipping_total = Decimal('0.00')
            if submission.get('shipping_method') and submission['shipping_method'].charge_incl_tax:
                shipping_total = Decimal(str(submission['shipping_method'].charge_incl_tax))
            
            subtotal_ex_vat = products_total + shipping_total
            vat_amount = (subtotal_ex_vat * Decimal('0.20')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            total_inc_vat = subtotal_ex_vat + vat_amount
            
            logger.info(f"🧮 VAT Calculation:")
            logger.info(f"  - Products ex VAT: £{products_total}")
            logger.info(f"  - Shipping ex VAT: £{shipping_total}")
            logger.info(f"  - Subtotal ex VAT: £{subtotal_ex_vat}")
            logger.info(f"  - VAT (20%): £{vat_amount}")
            logger.info(f"  - Total inc VAT: £{total_inc_vat}")
            
            # Get IDs for session storage
            user_id = submission.get('user').pk if submission.get('user') else None
            shipping_address_id = submission.get('shipping_address').id if submission.get('shipping_address') else None
            billing_address_id = submission.get('billing_address').id if submission.get('billing_address') else None
            shipping_method_code = submission.get('shipping_method').code if submission.get('shipping_method') else None
            
            logger.info(f"🔗 Session storage IDs:")
            logger.info(f"  - User ID: {user_id}")
            logger.info(f"  - Basket ID: {submission['basket'].id}")
            logger.info(f"  - Shipping address ID: {shipping_address_id}")
            logger.info(f"  - Billing address ID: {billing_address_id}")
            logger.info(f"  - Shipping method code: {shipping_method_code}")
            
            # Store submission data for later order creation (using VAT-inclusive total)
            request.session['worldpay_gateway_submission'] = {
                'order_number': order_number,
                'order_total': float(total_inc_vat),  # Use VAT-inclusive total
                'currency': str(submission['order_total'].currency),
                'submission_data': {
                    'user': user_id,
                    'basket_id': submission['basket'].id,
                    'shipping_address_id': shipping_address_id,
                    'billing_address_id': billing_address_id,
                    'shipping_method_code': shipping_method_code,
                    'shipping_charge': float(shipping_total),  # Store the actual shipping charge!
                }
            }
            
            logger.info(f"✅ Stored Gateway submission for order {order_number}")
            logger.info(f"💰 Order total: {submission['order_total'].currency} {total_inc_vat} (incl. UK VAT)")
            
            # Redirect to card details form
            return HttpResponseRedirect(reverse('payment:worldpay-gateway-card-form'))
            
        except Exception as e:
            logger.error(f"Error preparing Gateway payment: {str(e)}")
            messages.error(request, _("An error occurred preparing your payment. Please try again."))
            return HttpResponseRedirect(reverse('checkout:payment-details'))


class WorldpayGatewayCardFormView(CheckoutSessionMixin, View):
    """
    View to collect card details for Gateway API payment
    """
    template_name = 'payment/worldpay_gateway_card_form.html'
    
    def get(self, request, *args, **kwargs):
        """
        Display card details form
        """
        # Check if we have a valid session
        session_data = request.session.get('worldpay_gateway_submission')
        if not session_data:
            logger.warning("No Gateway payment session found")
            messages.error(request, _("Your payment session has expired. Please start again."))
            return HttpResponseRedirect(reverse('checkout:payment-details'))
        
        form = WorldpayCardDetailsForm()
        
        context = {
            'form': form,
            'order_total': session_data['order_total'],
            'currency': session_data['currency'],
            'order_number': session_data['order_number']
        }
        
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        """
        Process card details and payment
        """
        logger.info("🎯 Starting Gateway payment processing")
        
        # Check session data
        session_data = request.session.get('worldpay_gateway_submission')
        if not session_data:
            logger.error("❌ No Gateway payment session found")
            messages.error(request, _("Your payment session has expired. Please start again."))
            return HttpResponseRedirect(reverse('checkout:payment-details'))
        
        logger.info(f"✅ Found session data for order: {session_data.get('order_number')}")
        logger.info(f"Session data keys: {list(session_data.keys())}")
        
        form = WorldpayCardDetailsForm(request.POST)
        logger.info(f"Form validation: {form.is_valid()}")
        
        if not form.is_valid():
            logger.error(f"❌ Form validation failed: {form.errors}")
            context = {
                'form': form,
                'order_total': session_data['order_total'],
                'currency': session_data['currency'],
                'order_number': session_data['order_number']
            }
            return render(request, self.template_name, context)
        
        logger.info("✅ Form is valid, proceeding with payment")
        
        try:
            # Check if order already exists (e.g., after reload/retry)
            order_number = session_data.get('order_number')
            try:
                order = Order.objects.get(number=order_number)
                logger.info(f"♻️ Order {order_number} already exists, reusing it")
            except Order.DoesNotExist:
                # Create the order first
                logger.info("🏗️ Creating order from session...")
                order = self._create_order_from_session(request, session_data)
                
                if not order:
                    logger.error("❌ Failed to create order")
                    raise Exception("Failed to create order")
                
                logger.info(f"✅ Order created successfully: {order.number}")
            
            # Process payment with Gateway API (with 3DS)
            facade = WorldpayGatewayFacade()
            card_data = form.cleaned_data
            
            logger.info(f"💳 Processing Gateway payment for order {order.number}")
            logger.info(f"Card data keys: {list(card_data.keys())}")
            logger.info(f"Card number (masked): {card_data['card_number'][:4]}****{card_data['card_number'][-4:]}")
            
            # Step 1: Perform 3DS authentication
            logger.info(f"🔒 Step 1: Performing 3DS authentication for order {order.number}")
            threeds_result = facade.authenticate_3ds(order, card_data, request)
            
            outcome = threeds_result.get('outcome')
            
            if outcome == 'challenged':
                # Challenge required - show 3DS challenge iframe
                challenge_url = threeds_result.get('challenge_url')
                challenge_jwt = threeds_result.get('challenge_jwt')
                logger.info(f"⚠️ 3DS challenge required for order {order.number}")
                logger.info(f"   Challenge URL: {challenge_url}")
                logger.info(f"   Challenge JWT: {challenge_jwt[:50]}..." if challenge_jwt else "No JWT")
                
                # Store order info and card data in session for after challenge
                challenge_session_data = {
                    'order_id': order.id,
                    'order_number': order.number,
                    'card_data': {
                        'card_number': card_data['card_number'],
                        'expiry_month': card_data['expiry_month'],
                        'expiry_year': card_data['expiry_year'],
                        'cvc': card_data['cvc'],
                        'cardholder_name': card_data['cardholder_name']
                    },
                    'authentication': threeds_result.get('authentication', {}),
                    'challenge_reference': threeds_result.get('challenge_reference')
                }
                
                request.session['threeds_challenge'] = challenge_session_data
                request.session.modified = True
                
                logger.info(f"   💾 Saving session data for order {order.number}")
                logger.info(f"   Session key before save: {request.session.session_key}")
                logger.info(f"   Session data keys before save: {list(request.session.keys())}")
                
                # Force save
                request.session.save()
                
                logger.info(f"   ✅ Session saved")
                logger.info(f"   Session key after save: {request.session.session_key}")
                
                # Verify it was saved
                test_data = request.session.get('threeds_challenge')
                logger.info(f"   Verification - threeds_challenge present: {test_data is not None}")
                if test_data:
                    logger.info(f"   Verification - order_id: {test_data.get('order_id')}")
                
                # Render challenge page with iframe
                context = {
                    'challenge_url': challenge_url,
                    'challenge_jwt': challenge_jwt,
                    'order': order,
                    'order_total': session_data['order_total'],
                    'currency': session_data['currency']
                }
                return render(request, 'payment/threeds_challenge.html', context)
            
            if not threeds_result.get('success'):
                outcome = threeds_result.get('outcome')
                    
                if outcome == 'unavailable':
                    # 3DS not available - proceed without it (may get soft decline)
                    logger.warning(f"⚠️ 3DS unavailable for order {order.number} - proceeding without 3DS")
                    authentication_data = None
                    
                else:
                    # 3DS failed
                    logger.error(f"❌ 3DS authentication failed for order {order.number}: {threeds_result.get('error_message')}")
                    messages.error(request, _("Card authentication failed: {error}").format(error=threeds_result.get('error_message')))
                    context = {
                        'form': form,
                        'order_total': session_data['order_total'],
                        'currency': session_data['currency'],
                        'order_number': session_data['order_number'],
                        'payment_error': threeds_result.get('error_message')
                    }
                    return render(request, self.template_name, context)
            else:
                # 3DS authenticated successfully
                authentication_data = threeds_result.get('authentication')
                logger.info(f"✅ 3DS authentication successful for order {order.number}")
            
            # Step 2: Process payment with 3DS authentication data
            logger.info(f"💰 Step 2: Processing payment authorization for order {order.number}")
            payment_result = facade.process_payment(order, card_data, authentication_data)
            
            logger.info(f"💰 Payment result: {payment_result}")
            logger.info(f"💰 Payment result type: {type(payment_result)}")
            logger.info(f"💰 Payment result success: {payment_result.get('success') if payment_result else 'None'}")
            
            # Check for None result
            if payment_result is None:
                logger.error(f"❌ Payment facade returned None for order {order.number}")
                messages.error(request, _("Payment processing failed: No response from payment gateway"))
                context = {
                    'form': form,
                    'order_total': session_data['order_total'],
                    'currency': session_data['currency'],
                    'order_number': session_data['order_number'],
                    'payment_error': 'Payment processing failed'
                }
                return render(request, self.template_name, context)
            
            if payment_result.get('success'):
                logger.info(f"✅ Payment successful for order {order.number}")
                logger.info(f"Payment ID: {payment_result.get('payment_id')}")
                
                # Payment source creation is handled by the facade
                
                # Set checkout session data for thank-you page
                request.session['checkout_order_id'] = order.id
                
                # Clear payment session data
                request.session.pop('worldpay_gateway_submission', None)
                
                messages.success(request, _("Payment successful! Your order has been placed."))
                return HttpResponseRedirect(reverse('checkout:thank-you'))
            
            else:
                logger.error(f"❌ Payment failed for order {order.number}: {payment_result.get('error_message')}")
                
                # Check if this was a test card error
                if payment_result.get('is_test_card', False):
                    error_message = "⚠️ Test cards cannot be used for real purchases. Please use a valid payment card to complete your order."
                    logger.warning(f"Test card attempted for order {order.number}")
                else:
                    error_message = payment_result.get('error_message', 'Payment processing failed')
                
                messages.error(request, _("Payment failed: {error}").format(error=error_message))
                
                # Return to card form with error
                context = {
                    'form': form,
                    'order_total': session_data['order_total'],
                    'currency': session_data['currency'],
                    'order_number': session_data['order_number'],
                    'payment_error': error_message,
                    'is_test_card_error': payment_result.get('is_test_card', False)
                }
                return render(request, self.template_name, context)
                
        except Exception as e:
            logger.error(f"💥 Critical error in payment processing: {str(e)}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            
            messages.error(request, _("An error occurred processing your payment. Please try again."))
            
            context = {
                'form': form,
                'order_total': session_data['order_total'],
                'currency': session_data['currency'],
                'order_number': session_data['order_number'],
                'payment_error': str(e)
            }
            return render(request, self.template_name, context)
    
    def _create_order_from_session(self, request, session_data):
        """
        Create the order from stored session data
        """
        try:
            logger.info("🔧 Starting order creation from session data")
            logger.info(f"Session data keys: {list(session_data.keys())}")
            logger.info(f"Submission data keys: {list(session_data['submission_data'].keys())}")
            
            # Reconstruct the submission data
            submission_data = session_data['submission_data']
            
            # Get user first (needed for strategy)
            user = None
            if submission_data['user']:
                try:
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    user = User.objects.get(pk=submission_data['user'])
                    logger.info(f"✅ Found user: {user.username if hasattr(user, 'username') else user.email}")
                except Exception as e:
                    logger.warning(f"⚠️ Could not load user: {str(e)}")
            else:
                logger.info("ℹ️ No user specified (guest checkout)")
            
            # Get the basket
            from oscar.core.loading import get_model
            Basket = get_model('basket', 'Basket')
            
            logger.info(f"Looking for basket with ID: {submission_data['basket_id']}")
            try:
                basket = Basket.objects.get(id=submission_data['basket_id'])
                logger.info(f"✅ Found basket: {basket.id}, items: {basket.num_items}")
                
                # CRITICAL: Assign strategy to basket BEFORE accessing any totals!
                from oscar.core.loading import get_class
                
                # Get the default strategy class directly
                try:
                    DefaultStrategy = get_class('partner.strategy', 'Default')
                    strategy = DefaultStrategy()
                    basket.strategy = strategy
                    logger.info(f"✅ Strategy assigned to basket: {strategy}")
                    logger.info(f"✅ Basket total: {basket.total_incl_tax}")
                except Exception as strategy_error:
                    logger.warning(f"⚠️ Could not get Default strategy: {strategy_error}")
                    # Fallback: create a minimal strategy manually
                    from oscar.apps.partner.strategy import Default as FallbackStrategy
                    strategy = FallbackStrategy()
                    basket.strategy = strategy
                    logger.info(f"✅ Fallback strategy assigned to basket: {strategy}")
                    logger.info(f"✅ Basket total with fallback: {basket.total_incl_tax}")
                
            except Basket.DoesNotExist:
                logger.error(f"❌ Basket not found with ID: {submission_data['basket_id']}")
                return None
            except Exception as e:
                logger.error(f"❌ Error loading basket or assigning strategy: {str(e)}")
                return None
            
            # Get addresses - create proper Oscar address instances
            shipping_address = None
            billing_address = None
            
            # Import the correct address models for orders
            from oscar.apps.order.models import ShippingAddress, BillingAddress
            
            if submission_data['shipping_address_id']:
                try:
                    from oscar.apps.address.models import UserAddress
                    user_address = UserAddress.objects.get(id=submission_data['shipping_address_id'])
                    logger.info(f"✅ Found user shipping address: {user_address.summary}")
                    
                    # Convert UserAddress to ShippingAddress for the order
                    shipping_address = ShippingAddress(
                        title=user_address.title,
                        first_name=user_address.first_name,
                        last_name=user_address.last_name,
                        line1=user_address.line1,
                        line2=user_address.line2,
                        line3=user_address.line3,
                        line4=user_address.line4,
                        state=user_address.state,
                        postcode=user_address.postcode,
                        country=user_address.country
                        # Note: phone_number is not a field on ShippingAddress model
                    )
                    shipping_address.save()  # Save to database first
                    logger.info(f"✅ Created shipping address for order: {shipping_address.summary}")
                except Exception as e:
                    logger.warning(f"⚠️ Could not load shipping address: {str(e)}")
            else:
                # Try to create shipping address from session data
                try:
                    checkout_data = request.session.get('checkout_data', {})
                    shipping_data = checkout_data.get('shipping', {}).get('new_address_fields', {})
                    
                    if shipping_data and shipping_data.get('line1'):
                        logger.info("🏗️ Creating shipping address from session data")
                        
                        # Import the address models
                        from oscar.apps.address.models import Country
                        
                        # Get country
                        country = None
                        if shipping_data.get('country_id'):
                            try:
                                country = Country.objects.get(iso_3166_1_a2=shipping_data['country_id'])
                            except Country.DoesNotExist:
                                logger.warning(f"Country not found: {shipping_data['country_id']}")
                        
                        # Create ShippingAddress directly for the order
                        shipping_address = ShippingAddress(
                            title=shipping_data.get('title', ''),
                            first_name=shipping_data.get('first_name', ''),
                            last_name=shipping_data.get('last_name', ''),
                            line1=shipping_data.get('line1', ''),
                            line2=shipping_data.get('line2', ''),
                            line3=shipping_data.get('line3', ''),
                            line4=shipping_data.get('line4', ''),
                            state=shipping_data.get('state', ''),
                            postcode=shipping_data.get('postcode', ''),
                            country=country
                            # Note: phone_number is not a field on ShippingAddress model
                        )
                        shipping_address.save()  # Save to database first
                        logger.info(f"✅ Created shipping address from session: {shipping_address.summary}")
                    
                except Exception as e:
                    logger.warning(f"⚠️ Could not create shipping address from session: {str(e)}")
            
            if submission_data['billing_address_id']:
                try:
                    from oscar.apps.address.models import UserAddress
                    user_address = UserAddress.objects.get(id=submission_data['billing_address_id'])
                    logger.info(f"✅ Found user billing address: {user_address.summary}")
                    
                    # Convert UserAddress to BillingAddress for the order
                    billing_address = BillingAddress(
                        title=user_address.title,
                        first_name=user_address.first_name,
                        last_name=user_address.last_name,
                        line1=user_address.line1,
                        line2=user_address.line2,
                        line3=user_address.line3,
                        line4=user_address.line4,
                        state=user_address.state,
                        postcode=user_address.postcode,
                        country=user_address.country
                        # Note: phone_number is not a field on BillingAddress model
                    )
                    billing_address.save()  # Save to database first
                    logger.info(f"✅ Created billing address for order: {billing_address.summary}")
                except Exception as e:
                    logger.warning(f"⚠️ Could not load billing address: {str(e)}")
            else:
                # Convert shipping address to billing address if not specified
                if shipping_address:
                    billing_address = BillingAddress(
                        title=shipping_address.title,
                        first_name=shipping_address.first_name,
                        last_name=shipping_address.last_name,
                        line1=shipping_address.line1,
                        line2=shipping_address.line2,
                        line3=shipping_address.line3,
                        line4=shipping_address.line4,
                        state=shipping_address.state,
                        postcode=shipping_address.postcode,
                        country=shipping_address.country
                        # Note: phone_number is not a field on BillingAddress model
                    )
                    billing_address.save()  # Save to database first
                    logger.info("ℹ️ Using shipping address as billing address")
            
            # Get shipping method with correct charge from session
            shipping_method = None
            shipping_charge = Decimal(str(submission_data.get('shipping_charge', '0.00')))
            logger.info(f"💰 Shipping charge from session: £{shipping_charge}")
            
            if submission_data.get('shipping_method_code'):
                try:
                    # Reconstruct shipping method with the stored charge
                    from oscar.apps.shipping.methods import FixedPrice
                    shipping_method = FixedPrice(charge_excl_tax=shipping_charge, charge_incl_tax=shipping_charge)
                    logger.info(f"✅ Using shipping method with charge £{shipping_charge}")
                except Exception as e:
                    logger.warning(f"⚠️ Could not create shipping method: {str(e)}")
            
            if not shipping_method:
                from oscar.apps.shipping.methods import FixedPrice
                shipping_method = FixedPrice(charge_excl_tax=shipping_charge, charge_incl_tax=shipping_charge)
                logger.info(f"ℹ️ Using fallback shipping method with charge £{shipping_charge}")
            
            # Try different order creation approaches
            logger.info("🔨 Attempting order creation...")
            
            # Method 1: Try OrderCreator
            try:
                from oscar.apps.order.utils import OrderCreator
                order_creator = OrderCreator()
                
                logger.info("📝 Order creation parameters:")
                logger.info(f"  - Basket: {basket}")
                logger.info(f"  - Total: {basket.total_incl_tax}")
                logger.info(f"  - Shipping method: {shipping_method}")
                logger.info(f"  - Shipping method type: {type(shipping_method)}")
                
                # Calculate shipping charge using the correct method
                shipping_total = None
                if shipping_method:
                    try:
                        # Try different possible methods for calculating shipping
                        if hasattr(shipping_method, 'calculate'):
                            shipping_total = shipping_method.calculate(basket)
                            logger.info(f"  - Shipping charge via calculate(): {shipping_total}")
                        elif hasattr(shipping_method, 'charge_incl_tax'):
                            from oscar.core import prices
                            shipping_charge = shipping_method.charge_incl_tax
                            shipping_total = prices.Price(
                                currency=basket.currency,
                                excl_tax=shipping_charge,
                                incl_tax=shipping_charge
                            )
                            logger.info(f"  - Shipping charge via charge_incl_tax: {shipping_total}")
                        else:
                            logger.warning(f"⚠️ Unknown shipping method attributes: {dir(shipping_method)}")
                            from oscar.core import prices
                            shipping_total = prices.Price(
                                currency=basket.currency,
                                excl_tax=0,
                                incl_tax=0
                            )
                    except Exception as e:
                        logger.warning(f"⚠️ Could not calculate shipping charge: {e}")
                        from oscar.core import prices
                        shipping_total = prices.Price(
                            currency=basket.currency,
                            excl_tax=0,
                            incl_tax=0
                        )
                else:
                    logger.info("  - No shipping method, charge = 0")
                    from oscar.core import prices
                    shipping_total = prices.Price(
                        currency=basket.currency,
                        excl_tax=0,
                        incl_tax=0
                    )
                
                # Create proper Price object for order total using VAT-calculated amount from session
                from oscar.core import prices
                
                # Use the VAT-inclusive total that was calculated and stored in the session
                vat_inclusive_amount = Decimal(str(session_data['order_total']))
                
                # For ex VAT, we'll use the basket total since that represents the pre-VAT amount
                order_total = prices.Price(
                    currency=basket.currency,
                    excl_tax=basket.total_excl_tax + (shipping_total.incl_tax or 0),
                    incl_tax=vat_inclusive_amount
                )
                
                logger.info(f"  - Order total (Price object): {order_total}")
                logger.info(f"  - VAT-inclusive amount from session: £{vat_inclusive_amount}")
                logger.info(f"  - Shipping total (Price object): {shipping_total}")
                
                logger.info(f"  - Shipping address: {shipping_address}")
                logger.info(f"  - Billing address: {billing_address}")
                logger.info(f"  - User: {user}")
                logger.info(f"  - Order number: {session_data['order_number']}")
                
                # Log the shipping details before order creation
                logger.info(f"🚚 Final shipping details for order creation:")
                logger.info(f"  - Shipping method: {shipping_method}")
                logger.info(f"  - Shipping charge: {shipping_total}")
                logger.info(f"  - Shipping method charge_incl_tax: {getattr(shipping_method, 'charge_incl_tax', 'N/A')}")
                
                order = order_creator.place_order(
                    basket=basket,
                    total=order_total,
                    shipping_method=shipping_method,
                    shipping_charge=shipping_total,
                    shipping_address=shipping_address,
                    billing_address=billing_address,
                    user=user,
                    order_number=session_data['order_number']
                )
                
                logger.info(f"✅ Successfully created order {order.number}")
                logger.info(f"📦 Order shipping cost: £{order.shipping_incl_tax}")
                return order
                
            except Exception as e:
                logger.error(f"❌ OrderCreator failed: {str(e)}")
                logger.error(f"Exception type: {type(e).__name__}")
                import traceback
                logger.error(f"Full traceback: {traceback.format_exc()}")
                
                # Method 2: Try simple Order model creation
                try:
                    logger.info("🔄 Trying direct Order model creation...")
                    from oscar.core.loading import get_model
                    Order = get_model('order', 'Order')
                    
                    # Calculate total including shipping
                    shipping_amount = shipping_total.incl_tax if shipping_total else Decimal('0.00')
                    order_total_with_shipping = basket.total_incl_tax + shipping_amount
                    
                    # Create basic order data
                    order_data = {
                        'number': session_data['order_number'],
                        'user': user,
                        'billing_address': billing_address,
                        'shipping_address': shipping_address,
                        'total_incl_tax': order_total_with_shipping,
                        'total_excl_tax': basket.total_excl_tax + shipping_amount,
                        'currency': basket.currency,
                        'status': 'Pending'
                    }
                    
                    # Only add shipping fields if they exist on the model
                    Order_model = Order
                    if hasattr(Order_model, '_meta'):
                        field_names = [f.name for f in Order_model._meta.get_fields()]
                        if 'shipping_incl_tax' in field_names:
                            order_data['shipping_incl_tax'] = shipping_amount
                        if 'shipping_excl_tax' in field_names:
                            order_data['shipping_excl_tax'] = shipping_amount
                        if 'shipping_method' in field_names and shipping_method:
                            order_data['shipping_method'] = shipping_method.name
                    
                    order = Order.objects.create(**order_data)
                    
                    logger.info(f"✅ Successfully created order via direct model: {order.number}")
                    logger.info(f"📦 Order total: £{order.total_incl_tax}")
                    return order
                    
                except Exception as e2:
                    logger.error(f"❌ Direct Order creation also failed: {str(e2)}")
                    import traceback
                    logger.error(f"Full traceback: {traceback.format_exc()}")
                    return None
            
        except Exception as e:
            logger.error(f"❌ Critical error in order creation: {str(e)}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return None


class WorldpayGatewaySuccessView(TemplateView):
    """
    Success page after Gateway payment
    """
    template_name = 'payment/worldpay_gateway_success.html'


class WorldpayGatewayFailureView(TemplateView):
    """
    Failure page for Gateway payment
    """
    template_name = 'payment/worldpay_gateway_failure.html'


@method_decorator(csrf_exempt, name='dispatch')
class ThreeDSCallbackView(CheckoutSessionMixin, View):
    """
    Callback view after 3DS challenge completion
    This view must be frameable for Cardinal Commerce 3DS return
    """
    @method_decorator(lambda view_func: lambda request, *args, **kwargs: view_func(request, *args, **kwargs))
    def dispatch(self, *args, **kwargs):
        response = super().dispatch(*args, **kwargs)
        # Allow this page to be loaded in iframe (remove X-Frame-Options)
        if hasattr(response, 'xframe_options_exempt'):
            response.xframe_options_exempt = True
        return response
    
    def _handle_callback(self, request):
        """
        Common callback handling for both GET and POST
        """
        logger.info("🔄 3DS challenge callback received")
        logger.info(f"   Method: {request.method}")
        logger.info(f"   User-Agent: {request.META.get('HTTP_USER_AGENT', 'Unknown')}")
        logger.info(f"   Referer: {request.META.get('HTTP_REFERER', 'None')}")
        logger.info(f"   GET params: {dict(request.GET)}")
        logger.info(f"   POST params: {dict(request.POST)}")
        
        # Cardinal Commerce posts back to this URL after challenge
        # We need to show iframe-friendly page that notifies parent
        if 'cardinalcommerce' in request.META.get('HTTP_REFERER', '').lower():
            logger.info("   Loading callback in iframe mode (from Cardinal)")
            return render(request, 'payment/threeds_callback_frame.html')
        
        # If called directly (from parent page after postMessage), process payment
        return None
    
    def get(self, request, *args, **kwargs):
        """
        Handle GET callback after 3DS challenge
        """
        logger.info("="*60)
        logger.info("GET CALLBACK STARTED")
        logger.info("="*60)
        
        iframe_response = self._handle_callback(request)
        if iframe_response:
            logger.info("   Returning iframe response")
            return iframe_response
        
        logger.info("   Not iframe mode - processing payment")
        
        # Get stored challenge data from session
        logger.info(f"   Session ID: {request.session.session_key}")
        logger.info(f"   Session age: {request.session.get_expiry_age()} seconds")
        logger.info(f"   Session keys: {list(request.session.keys())}")
        
        # Try to access session directly from database
        from django.contrib.sessions.models import Session
        try:
            session_obj = Session.objects.get(session_key=request.session.session_key)
            logger.info(f"   📊 Database session expires: {session_obj.expire_date}")
            session_data = session_obj.get_decoded()
            logger.info(f"   📊 Database session keys: {list(session_data.keys())}")
            logger.info(f"   📊 Database has threeds_challenge: {'threeds_challenge' in session_data}")
        except Session.DoesNotExist:
            logger.error("   ❌ Session not found in database!")
        except Exception as e:
            logger.error(f"   ❌ Error reading session from database: {e}")
        
        challenge_data = request.session.get('threeds_challenge')
        logger.info(f"   Challenge data present in request.session: {challenge_data is not None}")
        
        if challenge_data:
            logger.info(f"   Challenge data keys: {list(challenge_data.keys())}")
            logger.info(f"   Order ID: {challenge_data.get('order_id')}")
            logger.info(f"   Order number: {challenge_data.get('order_number')}")
        
        if not challenge_data:
            logger.error("❌ No challenge data in session - PAYMENT WILL FAIL")
            logger.error(f"   All session data: {dict(request.session)}")
            messages.error(request, _("Your payment session has expired. Please try again."))
            return HttpResponseRedirect(reverse('checkout:payment-details'))
        
        logger.info(f"✅ Found challenge data for order: {challenge_data['order_number']}")
        
        try:
            # Get the order
            order = Order.objects.get(id=challenge_data['order_id'])
            
            # Get card data and authentication
            card_data = challenge_data['card_data']
            authentication_data = challenge_data['authentication']
            
            # Process payment with the authenticated 3DS data
            facade = WorldpayGatewayFacade()
            logger.info(f"💰 Processing payment after 3DS challenge for order {order.number}")
            
            payment_result = facade.process_payment(order, card_data, authentication_data)
            
            if payment_result and payment_result.get('success'):
                logger.info(f"✅ Payment successful after 3DS challenge for order {order.number}")
                
                # Clear session data
                request.session.pop('threeds_challenge', None)
                request.session.pop('worldpay_gateway_submission', None)
                request.session['checkout_order_id'] = order.id
                
                messages.success(request, _("Payment successful! Your order has been placed."))
                return HttpResponseRedirect(reverse('checkout:thank-you'))
            
            else:
                logger.error(f"❌ Payment failed after 3DS challenge for order {order.number}")
                error_msg = payment_result.get('error_message', 'Payment failed') if payment_result else 'Payment processing error'
                messages.error(request, _("Payment failed: {error}").format(error=error_msg))
                
                # Clear challenge data but keep order for retry
                request.session.pop('threeds_challenge', None)
                return HttpResponseRedirect(reverse('checkout:payment-details'))
                
        except Exception as e:
            logger.error(f"❌ Error in 3DS callback: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            
            messages.error(request, _("An error occurred processing your payment. Please try again."))
            return HttpResponseRedirect(reverse('checkout:payment-details'))
    
    def post(self, request, *args, **kwargs):
        """
        Handle POST callback after 3DS challenge (Cardinal Commerce posts back)
        """
        iframe_response = self._handle_callback(request)
        if iframe_response:
            return iframe_response
        
        # If not iframe mode, handle same as GET
        return self.get(request, *args, **kwargs)


class WorldpayDebugConfigView(View):
    """
    Debug view to check Worldpay configuration
    """
    def get(self, request):
        import os
        from django.conf import settings
        from .gateway_facade import WorldpayGatewayFacade
        
        facade = WorldpayGatewayFacade()
        
        debug_info = {
            'env_test_mode': os.getenv('WORLDPAY_TEST_MODE', 'NOT SET'),
            'settings_test_mode': getattr(settings, 'WORLDPAY_TEST_MODE', 'NOT SET'),
            'gateway_url': getattr(settings, 'WORLDPAY_GATEWAY_URL', 'NOT SET'),
            'facade_api_url': facade.api_url,
            'test_url': 'https://try.access.worldpay.com/payments/authorizations',
            'live_url': 'https://access.worldpay.com/payments/authorizations',
        }
        
        # Determine current mode
        if facade.api_url == debug_info['test_url']:
            debug_info['current_mode'] = 'TEST'
        elif facade.api_url == debug_info['live_url']:
            debug_info['current_mode'] = 'LIVE'
        else:
            debug_info['current_mode'] = 'UNKNOWN'
        
        return JsonResponse(debug_info)

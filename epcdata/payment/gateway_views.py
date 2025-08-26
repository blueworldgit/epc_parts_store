"""
Gateway API views for Worldpay direct payment processing
"""
import logging
from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import View, TemplateView
from django.views.decorators.csrf import csrf_exempt
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
            generator = OrderNumberGenerator()
            base_order_number = generator.order_number(submission['basket'])
            
            # Add timestamp to ensure uniqueness in case of retries
            timestamp = int(time.time() % 10000)  # Last 4 digits of timestamp
            order_number = f"{base_order_number}-{timestamp}"
            
            logger.info(f"🎯 Generated unique order number: {order_number}")
            logger.info(f"📦 Basket details: ID={submission['basket'].id}, items={submission['basket'].num_items}, total={submission['basket'].total_incl_tax}")
            
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
            
            # Store submission data for later order creation
            request.session['worldpay_gateway_submission'] = {
                'order_number': order_number,
                'order_total': float(submission['order_total'].incl_tax),
                'currency': str(submission['order_total'].currency),
                'submission_data': {
                    'user': user_id,
                    'basket_id': submission['basket'].id,
                    'shipping_address_id': shipping_address_id,
                    'billing_address_id': billing_address_id,
                    'shipping_method_code': shipping_method_code,
                }
            }
            
            logger.info(f"✅ Stored Gateway submission for order {order_number}")
            logger.info(f"💰 Order total: {submission['order_total'].currency} {submission['order_total'].incl_tax}")
            
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
            # Create the order first
            logger.info("🏗️ Creating order from session...")
            order = self._create_order_from_session(request, session_data)
            
            if not order:
                logger.error("❌ Failed to create order")
                raise Exception("Failed to create order")
            
            logger.info(f"✅ Order created successfully: {order.number}")
            
            # Process payment with Gateway API
            facade = WorldpayGatewayFacade()
            card_data = form.cleaned_data
            
            logger.info(f"💳 Processing Gateway payment for order {order.number}")
            logger.info(f"Card data keys: {list(card_data.keys())}")
            logger.info(f"Card number (masked): {card_data['card_number'][:4]}****{card_data['card_number'][-4:]}")
            
            payment_result = facade.process_payment(order, card_data)
            
            logger.info(f"💰 Payment result: {payment_result.get('success')}")
            
            if payment_result['success']:
                logger.info(f"✅ Payment successful for order {order.number}")
                logger.info(f"Payment ID: {payment_result.get('payment_id')}")
                
                # Create payment source to link payment to order
                logger.info("🔗 Creating payment source...")
                self._create_payment_source(order, payment_result, card_data)
                
                # Clear session data
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
            
            # Get shipping method
            shipping_method = None
            if submission_data.get('shipping_method_code'):
                try:
                    # Try to reconstruct shipping method
                    from oscar.apps.shipping.methods import FixedPrice
                    from decimal import Decimal
                    shipping_method = FixedPrice(charge_excl_tax=Decimal('0'), charge_incl_tax=Decimal('0'))
                    logger.info(f"✅ Using default shipping method")
                except Exception as e:
                    logger.warning(f"⚠️ Could not create shipping method: {str(e)}")
            
            if not shipping_method:
                from oscar.apps.shipping.methods import FixedPrice
                from decimal import Decimal
                shipping_method = FixedPrice(charge_excl_tax=Decimal('0'), charge_incl_tax=Decimal('0'))
                logger.info("ℹ️ Using fallback free shipping method")
            
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
                
                # Create proper Price object for order total
                from oscar.core import prices
                order_total = prices.Price(
                    currency=basket.currency,
                    excl_tax=basket.total_excl_tax,
                    incl_tax=basket.total_incl_tax
                )
                
                logger.info(f"  - Order total (Price object): {order_total}")
                logger.info(f"  - Shipping total (Price object): {shipping_total}")
                
                logger.info(f"  - Shipping address: {shipping_address}")
                logger.info(f"  - Billing address: {billing_address}")
                logger.info(f"  - User: {user}")
                logger.info(f"  - Order number: {session_data['order_number']}")
                
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
                    
                    order = Order.objects.create(
                        number=session_data['order_number'],
                        user=user,
                        billing_address=billing_address,
                        shipping_address=shipping_address,
                        total_incl_tax=basket.total_incl_tax,
                        total_excl_tax=basket.total_excl_tax,
                        currency=basket.currency,
                        status='Pending'
                    )
                    
                    logger.info(f"✅ Successfully created order via direct model: {order.number}")
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

    def _create_payment_source(self, order, payment_result, card_data):
        """
        Create payment source to link the payment to the order
        """
        try:
            from oscar.apps.payment.models import Source, SourceType
            
            logger.info(f"🔗 Creating payment source for order {order.number}")
            
            # Get or create Worldpay Gateway source type
            source_type, created = SourceType.objects.get_or_create(
                name='Worldpay Gateway',
                defaults={'code': 'worldpay-gateway'}
            )
            
            if created:
                logger.info("📝 Created new SourceType: Worldpay Gateway")
            
            # Create the payment source
            source = Source.objects.create(
                source_type=source_type,
                currency='GBP',
                amount_allocated=order.total_incl_tax,
                amount_debited=order.total_incl_tax,
                reference=payment_result.get('payment_id', ''),
                label=f"****{card_data.get('card_number', '')[-4:]}"
            )
            
            # Link to order
            order.sources.add(source)
            
            # Create transaction record
            from oscar.apps.payment.models import Transaction
            
            transaction = Transaction.objects.create(
                source=source,
                txn_type='Authorisation',
                amount=order.total_incl_tax,
                reference=payment_result.get('payment_id', ''),
                status='Complete'
            )
            
            logger.info(f"✅ Payment source created successfully: {source.id}")
            logger.info(f"✅ Transaction created: {transaction.id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to create payment source: {str(e)}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")


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

"""
Custom checkout views for Worldpay Hosted Payment Pages integration
"""
from oscar.apps.checkout.views import *  # noqa
from oscar.apps.checkout.views import ShippingMethodView as BaseShippingMethodView
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponseRedirect
import logging

from payment.forms import WorldpayPaymentDetailsForm
from .forms import UKOnlyShippingAddressForm

logger = logging.getLogger(__name__)


class ShippingMethodView(BaseShippingMethodView):
    """
    Custom shipping method view to ensure proper integration with weight-based shipping
    """
    template_name = 'oscar/checkout/shipping_methods.html'
    
    def get_available_shipping_methods(self):
        """
        Get available shipping methods from our custom repository
        """
        from shipping.repository import Repository
        repository = Repository()
        return repository.get_available_shipping_methods(
            basket=self.request.basket,
            user=self.request.user,
            shipping_addr=self.get_shipping_address(self.request.basket)
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Ensure available methods are properly passed to template
        if not context.get('available_methods'):
            context['available_methods'] = self.get_available_shipping_methods()
            
        logger.info(f"ShippingMethodView context: available_methods = {context.get('available_methods')}")
        return context

    def post(self, request, *args, **kwargs):
        """
        Handle shipping method selection and save details to session
        """
        logger.info("🚚 Custom ShippingMethodView.post called")
        logger.info(f"POST data: {request.POST}")
        
        # Let the parent handle the main logic first
        response = super().post(request, *args, **kwargs)
        
        # After successful processing, save shipping details for order creation
        try:
            # Get the selected shipping method from checkout session
            if hasattr(self, 'checkout_session'):
                shipping_method = self.checkout_session.shipping_method()
                logger.info(f"📦 Selected shipping method: {shipping_method}")
                
                if shipping_method and request.basket:
                    # Calculate the charge for this specific basket
                    try:
                        if hasattr(shipping_method, 'calculate'):
                            charge = shipping_method.calculate(request.basket)
                            logger.info(f"💰 Calculated shipping charge: £{charge.incl_tax}")
                            
                            # Store in session for payment gateway
                            request.session['shipping_method_details'] = {
                                'code': getattr(shipping_method, 'code', 'weight_based'),
                                'name': getattr(shipping_method, 'name', 'Standard Shipping'),
                                'charge_incl_tax': float(charge.incl_tax) if charge else 0.00,
                                'charge_excl_tax': float(charge.excl_tax) if charge else 0.00,
                            }
                            logger.info(f"✅ Saved shipping details to session: {request.session['shipping_method_details']}")
                            
                        else:
                            logger.warning("⚠️ Shipping method has no calculate() method")
                            
                    except Exception as calc_error:
                        logger.warning(f"⚠️ Could not calculate shipping charge: {calc_error}")
                        
        except Exception as e:
            logger.warning(f"⚠️ Error saving shipping method to session: {e}")
        
        return response


class PaymentDetailsView(PaymentDetailsView):
    """
    Custom payment details view that integrates with Worldpay Hosted Payments
    """
    template_name = 'oscar/checkout/payment_details.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        logger.info("Custom PaymentDetailsView.get_context_data called")
        
        # Add Worldpay payment form to context
        context['payment_forms'] = [WorldpayPaymentDetailsForm()]
        
        # Add precise VAT calculations using precise_money
        try:
            from decimal import Decimal, ROUND_HALF_UP
            
            # Get basket and shipping totals
            basket_total = context.get('basket', self.request.basket).total_incl_tax or Decimal('0')
            shipping_method = context.get('shipping_method')
            shipping_total = Decimal('0')
            
            if shipping_method and hasattr(shipping_method, 'charge_incl_tax'):
                shipping_total = shipping_method.charge_incl_tax or Decimal('0')
            
            # Calculate with precise decimal arithmetic
            subtotal_ex_vat = basket_total + shipping_total
            vat_amount = (subtotal_ex_vat * Decimal('0.20')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            total_inc_vat = (subtotal_ex_vat + vat_amount).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
            # Add to context
            context['vat_calculations'] = {
                'subtotal_ex_vat': subtotal_ex_vat,
                'vat_amount': vat_amount,
                'total_inc_vat': total_inc_vat,
            }
            
            logger.info(f"VAT calculations: subtotal={subtotal_ex_vat}, vat={vat_amount}, total={total_inc_vat}")
            
        except Exception as e:
            logger.error(f"Error calculating VAT: {e}")
            context['vat_calculations'] = {
                'subtotal_ex_vat': Decimal('0'),
                'vat_amount': Decimal('0'),
                'total_inc_vat': Decimal('0'),
            }
        
        # Debug: log what's in the context
        logger.info(f"Payment forms added to context: {len(context['payment_forms'])}")
        
        return context
    
    def post(self, request, *args, **kwargs):
        logger.info("Custom PaymentDetailsView.post called")
        logger.info(f"POST data: {request.POST}")
        logger.info(f"Request method: {request.method}")
        logger.info(f"Request path: {request.path}")
        
        # Check if this is a payment method submission
        if 'payment_method' not in request.POST:
            logger.warning("No payment_method in POST data, treating as invalid form")
            messages.error(request, _("Please select a payment method"))
            return self.get(request, *args, **kwargs)
        
        # Handle form submission
        form = WorldpayPaymentDetailsForm(request.POST)
        logger.info(f"Form created with data: {form.data}")
        logger.info(f"Form is bound: {form.is_bound}")
        
        if form.is_valid():
            # Store payment method in session
            request.session['payment_method'] = form.cleaned_data['payment_method']
            
            logger.info(f"Payment method selected: {form.cleaned_data['payment_method']}")
            logger.info("Form is valid, preparing redirect")
            
            # Route to appropriate payment handler
            payment_method = form.cleaned_data['payment_method']
            
            if payment_method == 'worldpay-gateway':
                logger.info("Redirecting to Gateway API payment processing")
                return HttpResponseRedirect(reverse('payment:worldpay-gateway-redirect'))
            else:
                logger.error(f"Unknown payment method: {payment_method}")
                messages.error(request, _("Please select a valid payment method"))
                return self.render_to_response(self.get_context_data())
        else:
            # Log form errors for debugging
            logger.error(f"Form validation failed. Errors: {form.errors}")
            logger.error(f"Form non-field errors: {form.non_field_errors}")
            logger.error(f"Form data was: {form.data}")
            logger.error(f"Form fields: {list(form.fields.keys())}")
        
        # If form is invalid, show errors and return to the same page
        logger.warning("Payment form validation failed, returning to payment details page")
        context = self.get_context_data(**kwargs)
        context['form_errors'] = form.errors if 'form' in locals() else None
        messages.error(request, _("Please select a payment method"))
        
        # Return the GET response with form errors
        return self.render_to_response(context)
    
    def get_success_url(self):
        # For hosted payments, we go directly to Worldpay
        return reverse('payment:worldpay-redirect')


class ShippingAddressView(ShippingAddressView):
    """
    Custom shipping address view that enforces UK-only shipping
    """
    form_class = UKOnlyShippingAddressForm
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['uk_only_message'] = "We currently only ship within the United Kingdom"
        return context

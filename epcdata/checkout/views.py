"""
Custom checkout views for Worldpay Hosted Payment Pages integration
"""
from oscar.apps.checkout.views import *  # noqa
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponseRedirect
import logging

from payment.forms import WorldpayPaymentDetailsForm

logger = logging.getLogger(__name__)


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

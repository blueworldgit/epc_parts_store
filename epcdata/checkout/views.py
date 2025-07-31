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
    Custom payment details view that integrates with Worldpay
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
        
        # Handle form submission
        form = WorldpayPaymentDetailsForm(request.POST)
        if form.is_valid():
            # Store payment method in session
            request.session['payment_method'] = form.cleaned_data['payment_method']
            
            logger.info(f"Payment method selected: {form.cleaned_data['payment_method']}")
            
            # For Worldpay, we need to place the order first, then redirect to payment
            if form.cleaned_data['payment_method'] == 'worldpay':
                # First, let's try to get to the preview page
                # We'll handle the actual payment redirect in the preview view
                return HttpResponseRedirect(self.get_success_url())
        
        # If form is invalid, show errors
        logger.warning("Payment form validation failed")
        messages.error(request, _("Please select a payment method"))
        return self.get(request, *args, **kwargs)
    
    def get_success_url(self):
        # Continue to preview step
        return reverse('checkout:preview')

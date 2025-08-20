"""
Payment views for Worldpay Hosted Payment Pages integration
"""
import logging
from django.contrib import messages
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import View, TemplateView
from oscar.apps.checkout.session import CheckoutSessionMixin
from oscar.core.loading import get_model, get_class

from .facade import WorldpayHostedFacade

logger = logging.getLogger(__name__)

Order = get_model('order', 'Order')
OrderPlacementMixin = get_class('checkout.mixins', 'OrderPlacementMixin')


class WorldpayRedirectView(OrderPlacementMixin, CheckoutSessionMixin, View):
    """
    View to handle redirection to Worldpay hosted payment page
    """
    
    def get(self, request, *args, **kwargs):
        """
        Create payment session and redirect to Worldpay hosted page
        """
        # Check pre-conditions for checkout
        try:
            submission = self.build_submission()
            logger.info(f"Built submission successfully")
            logger.info(f"Submission keys: {list(submission.keys())}")
            logger.info(f"Order total: {submission['order_total']}")
        except Exception as e:
            logger.warning(f"Checkout submission failed: {str(e)}")
            import traceback
            traceback.print_exc()
            messages.error(request, _("Your checkout session has expired. Please start again."))
            return HttpResponseRedirect(reverse('checkout:index'))
        
        # Check if payment is required
        if not submission['order_total'].incl_tax:
            logger.info("No payment required for this order")
            messages.info(request, _("No payment is required for this order."))
            return HttpResponseRedirect(reverse('checkout:preview'))
        
        # Create a temporary order for payment processing
        # We'll create the actual order after successful payment
        try:
            logger.info("Creating temporary order data for payment")
            
            # Generate a unique order number for this payment session
            from oscar.apps.order.utils import OrderNumberGenerator
            generator = OrderNumberGenerator()
            order_number = generator.order_number(submission['basket'])
            
            # Create a simple order-like object for payment processing
            class TempOrder:
                def __init__(self, submission, number):
                    self.number = number
                    self.total_incl_tax = submission['order_total'].incl_tax
                    self.currency = submission['order_total'].currency
                    self.email = submission.get('order_kwargs', {}).get('guest_email', 'guest@example.com')
                    self.user = submission.get('user')
                    self.billing_address = submission.get('billing_address')
            
            temp_order = TempOrder(submission, order_number)
            logger.info(f"Created temporary order: {temp_order.number}")
            
            # Store submission in session for later order creation
            request.session['worldpay_submission'] = {
                'order_number': order_number,
                'order_total': float(submission['order_total'].incl_tax),
                'currency': str(submission['order_total'].currency),
            }
            
            # Create payment session with Worldpay
            facade = WorldpayHostedFacade()
            payment_url = facade.create_payment_session(temp_order, request)
            
            if payment_url:
                logger.info(f"Redirecting to Worldpay payment page for order {temp_order.number}")
                return HttpResponseRedirect(payment_url)
            else:
                logger.error("Failed to create Worldpay payment session")
                messages.error(request, _("Unable to process payment. Please try again."))
                return HttpResponseRedirect(reverse('checkout:payment-details'))
                
        except Exception as e:
            logger.error(f"Error in WorldpayRedirectView: {str(e)}")
            import traceback
            traceback.print_exc()
            messages.error(request, _("An error occurred processing your payment. Please try again."))
            return HttpResponseRedirect(reverse('checkout:payment-details'))


class WorldpayCallbackView(View):
    """
    Handle callbacks from Worldpay (not used in hosted payment pages)
    This is kept for compatibility but may not be needed for API-based hosted payments
    """
    
    def post(self, request, *args, **kwargs):
        """
        Handle POST callback from Worldpay
        """
        logger.info("Worldpay callback received")
        # For hosted payment pages, callbacks are handled via result URLs
        # This view may not be used
        return HttpResponseRedirect(reverse('checkout:thank-you'))


class WorldpaySuccessView(TemplateView):
    """
    Handle successful payment return from Worldpay
    """
    template_name = 'payment/worldpay_success.html'
    
    def get(self, request, *args, **kwargs):
        """
        Handle successful payment return
        """
        logger.info("Worldpay success callback received")
        
        # Handle the payment callback
        facade = WorldpayHostedFacade()
        order = facade.handle_payment_callback(request, status='success')
        
        if order:
            logger.info(f"Payment successful for order {order.number}")
            messages.success(request, _("Payment successful! Thank you for your order."))
            
            # Clear the checkout session
            if hasattr(self, 'checkout_session'):
                self.checkout_session.flush()
            
            # Redirect to thank you page with order details
            return HttpResponseRedirect(
                reverse('checkout:thank-you') + f'?order_number={order.number}'
            )
        else:
            logger.error("Failed to process successful payment callback")
            messages.error(request, _("There was an issue confirming your payment. Please contact support."))
            return HttpResponseRedirect(reverse('checkout:payment-details'))


class WorldpayFailureView(TemplateView):
    """
    Handle failed payment return from Worldpay
    """
    template_name = 'payment/worldpay_failure.html'
    
    def get(self, request, *args, **kwargs):
        """
        Handle failed payment return
        """
        logger.info("Worldpay failure callback received")
        
        # Handle the payment callback
        facade = WorldpayHostedFacade()
        order = facade.handle_payment_callback(request, status='failure')
        
        if order:
            logger.info(f"Payment failed for order {order.number}")
            messages.error(request, _("Payment failed. Please try again or use a different payment method."))
        else:
            logger.error("Failed to process payment failure callback")
            messages.error(request, _("Payment failed. Please try again."))
        
        return HttpResponseRedirect(reverse('checkout:payment-details'))


class WorldpayCancelView(TemplateView):
    """
    Handle cancelled payment return from Worldpay
    """
    template_name = 'payment/worldpay_cancel.html'
    
    def get(self, request, *args, **kwargs):
        """
        Handle cancelled payment return
        """
        logger.info("Worldpay cancel callback received")
        
        # Handle the payment callback
        facade = WorldpayHostedFacade()
        order = facade.handle_payment_callback(request, status='cancelled')
        
        if order:
            logger.info(f"Payment cancelled for order {order.number}")
            messages.info(request, _("Payment was cancelled. You can try again when ready."))
        else:
            logger.warning("No order found for cancelled payment")
            messages.info(request, _("Payment was cancelled."))
        
        return HttpResponseRedirect(reverse('checkout:payment-details'))

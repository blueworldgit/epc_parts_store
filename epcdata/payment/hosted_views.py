import logging
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.generic import View
from django.utils.translation import gettext_lazy as _

from oscar.core.loading import get_model, get_class
from oscar.apps.checkout.session import CheckoutSessionMixin
from oscar.apps.basket.models import Basket

from .hosted_checkout_facade import WorldpayHostedCheckoutFacade
from .forms import WorldpayHostedCheckoutForm

Order = get_model('order', 'Order')
OrderPlacementMixin = get_class('checkout.mixins', 'OrderPlacementMixin')

logger = logging.getLogger(__name__)


class PaymentMethodSelectionView(CheckoutSessionMixin, View):
    """
    Allow users to choose between hosted checkout and access checkout
    """
    template_name = 'payment/payment_method_selection.html'
    
    def get(self, request, *args, **kwargs):
        """Display payment method selection"""
        # Basic validation - ensure we have a basket with items
        if not request.basket or request.basket.is_empty:
            messages.error(request, _('Your basket is empty.'))
            return redirect('basket:summary')
        
        # Get order totals
        try:
            order_total = request.basket.total_incl_tax
            if order_total <= 0:
                messages.error(request, _('Order total must be greater than zero.'))
                return redirect('basket:summary')
        except Exception as e:
            logger.error(f"Error calculating order total: {str(e)}")
            messages.error(request, _('Error calculating order total.'))
            return redirect('basket:summary')
        
        context = {
            'order_total': order_total,
            'basket': request.basket,
        }
        
        return render(request, self.template_name, context)


class WorldpayHostedCheckoutView(CheckoutSessionMixin, View):
    """
    Handle Worldpay Hosted Payment Pages checkout
    This redirects users to Worldpay's hosted payment page
    """
    template_name = 'payment/worldpay_hosted_checkout.html'
    
    def get(self, request, *args, **kwargs):
        """Display the hosted checkout redirect form"""
        # Basic validation - ensure we have a basket with items
        if not request.basket or request.basket.is_empty:
            messages.error(request, _('Your basket is empty.'))
            return redirect('basket:summary')
        
        # Get order totals
        try:
            order_total = request.basket.total_incl_tax
            if order_total <= 0:
                messages.error(request, _('Order total must be greater than zero.'))
                return redirect('basket:summary')
        except Exception as e:
            logger.error(f"Error calculating order total: {str(e)}")
            messages.error(request, _('Error calculating order total.'))
            return redirect('basket:summary')
        
        # Generate a unique order number for this checkout attempt
        order_number = self.generate_order_number(request)
        
        # Create payment data for Worldpay
        payment_data = WorldpayHostedCheckoutFacade.create_hosted_payment_data(
            order_total=order_total,
            order_number=order_number,
            request=request
        )
        
        # Create form with payment data
        form = WorldpayHostedCheckoutForm(initial=payment_data)
        
        context = {
            'form': form,
            'order_total': order_total,
            'order_number': order_number,
            'payment_url': WorldpayHostedCheckoutFacade.get_hosted_payment_url(),
            'basket': request.basket,
        }
        
        return render(request, self.template_name, context)
    
    def generate_order_number(self, request):
        """Generate a unique order number"""
        from datetime import datetime
        import uuid
        
        # Create a unique order number using timestamp and UUID
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        return f"WP{timestamp}{unique_id}"


@method_decorator(csrf_exempt, name='dispatch')
class WorldpayHostedCallbackView(OrderPlacementMixin, View):
    """
    Handle the callback from Worldpay after payment processing
    """
    
    def post(self, request, *args, **kwargs):
        """Process the callback from Worldpay"""
        logger.info("Received Worldpay hosted checkout callback")
        logger.info(f"POST data: {request.POST}")
        
        try:
            # Process the callback data
            success, result = WorldpayHostedCheckoutFacade.process_callback_data(request.POST)
            
            if success:
                # Payment was successful
                transaction_data = result
                order_number = transaction_data['order_number']
                transaction_id = transaction_data['transaction_id']
                
                logger.info(f"Payment successful for order {order_number}")
                
                # Here you would typically:
                # 1. Create the order in your system
                # 2. Mark the payment as complete
                # 3. Clear the basket
                # 4. Send confirmation emails
                
                # For now, we'll just log the success
                logger.info(f"Transaction {transaction_id} completed successfully")
                
                # Worldpay expects a simple response
                return HttpResponse("OK")
                
            else:
                # Payment failed
                error_message = result
                logger.error(f"Payment callback failed: {error_message}")
                
                # Worldpay expects a simple response even for failures
                return HttpResponse("FAILED")
                
        except Exception as e:
            logger.error(f"Error processing Worldpay callback: {str(e)}")
            return HttpResponse("ERROR")


class WorldpayHostedSuccessView(View):
    """
    Handle successful payment return from Worldpay
    """
    
    def get(self, request, *args, **kwargs):
        """Handle successful payment return"""
        logger.info("User returned from successful Worldpay payment")
        
        # Get transaction details from URL parameters
        transaction_id = request.GET.get('transId', '')
        order_number = request.GET.get('cartId', '')
        
        messages.success(
            request, 
            _('Payment completed successfully! Transaction ID: {transaction_id}').format(
                transaction_id=transaction_id
            )
        )
        
        # Redirect to order confirmation or checkout complete page
        return redirect('checkout:thank-you')


class WorldpayHostedFailureView(View):
    """
    Handle failed payment return from Worldpay
    """
    
    def get(self, request, *args, **kwargs):
        """Handle failed payment return"""
        logger.info("User returned from failed Worldpay payment")
        
        # Get error details from URL parameters
        order_number = request.GET.get('cartId', '')
        
        messages.error(
            request, 
            _('Payment was not completed. Please try again or use a different payment method.')
        )
        
        # Redirect back to payment selection or basket
        return redirect('checkout:payment-method')

import logging
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from django.utils.translation import gettext_lazy as _

from oscar.core.loading import get_model, get_class
from oscar.apps.checkout.session import CheckoutSessionMixin

from .facade import Facade
from .forms import WorldpayRedirectForm

Order = get_model('order', 'Order')
OrderPlacementMixin = get_class('checkout.mixins', 'OrderPlacementMixin')

logger = logging.getLogger(__name__)


class WorldpayRedirectView(CheckoutSessionMixin, View):
    """
    Redirect user to Worldpay Hosted Payment Page
    """
    template_name = 'payment/worldpay_redirect.html'
    
    def get(self, request):
        # Get order details from session
        submission = self.build_submission()
        if not submission['order_total'].incl_tax:
            # Free order, skip payment
            return redirect('checkout:preview')
        
        # Generate Worldpay form data
        form_data = Facade.get_form_data(
            order_number=submission['order_number'],
            amount=submission['order_total'].incl_tax,
            currency=submission['order_total'].currency,
            user=request.user,
            request=request
        )
        
        # Create form with pre-filled data
        form = WorldpayRedirectForm(initial=form_data)
        
        context = {
            'form': form,
            'worldpay_url': Facade.get_redirect_url(),
            'order_total': submission['order_total'],
        }
        
        return render(request, self.template_name, context)


@method_decorator(csrf_exempt, name='dispatch')
class WorldpayCallbackView(OrderPlacementMixin, View):
    """
    Handle callback from Worldpay after payment
    """
    
    def post(self, request):
        # Get parameters from Worldpay
        params = request.POST.dict()
        
        logger.info(f"Worldpay callback received: {params}")
        
        # Verify signature if configured
        if not Facade.verify_callback_signature(params):
            logger.error("Invalid signature in Worldpay callback")
            return HttpResponse("Invalid signature", status=400)
        
        # Get payment status
        trans_status = params.get('transStatus')
        cart_id = params.get('cartId')
        amount = params.get('amount')
        trans_id = params.get('transId')
        
        if trans_status == 'Y':  # Payment successful
            try:
                # Try to get existing order
                try:
                    order = Order.objects.get(number=cart_id)
                    logger.info(f"Payment successful for existing order {cart_id}")
                except Order.DoesNotExist:
                    logger.error(f"Order {cart_id} not found for successful payment")
                    return HttpResponse("Order not found", status=404)
                
                # Create payment source
                source = Facade.create_payment_source(order, trans_id, amount)
                
                # Record payment
                self.record_payment(order, source, amount)
                
                logger.info(f"Payment recorded for order {cart_id}, transaction {trans_id}")
                
            except Exception as e:
                logger.error(f"Error processing successful payment: {e}")
                return HttpResponse("Error processing payment", status=500)
                
        elif trans_status == 'C':  # Payment cancelled
            logger.info(f"Payment cancelled for order {cart_id}")
            
        else:  # Payment failed
            logger.warning(f"Payment failed for order {cart_id}: {trans_status}")
        
        return HttpResponse("OK")
    
    def record_payment(self, order, source, amount):
        """
        Record the payment against the order
        """
        # Add source to order
        order.sources.add(source)
        
        # Update order status if needed
        order.set_status('Paid')
        
        logger.info(f"Payment of {amount} recorded for order {order.number}")


class WorldpaySuccessView(View):
    """
    Handle successful payment return from Worldpay
    """
    
    def get(self, request):
        messages.success(request, _("Payment successful! Your order has been confirmed."))
        return redirect('checkout:thank-you')


class WorldpayFailureView(View):
    """
    Handle failed payment return from Worldpay
    """
    
    def get(self, request):
        messages.error(request, _("Payment failed. Please try again or use a different payment method."))
        return redirect('checkout:payment-details')


class WorldpayCancelView(View):
    """
    Handle cancelled payment return from Worldpay
    """
    
    def get(self, request):
        messages.warning(request, _("Payment was cancelled. Please complete your payment to finish your order."))
        return redirect('checkout:payment-details')

"""
Debug checkout flow
"""
from django.http import HttpResponse
from django.views.generic import View
from django.shortcuts import render
from oscar.apps.checkout.session import CheckoutSessionMixin
from oscar.core.loading import get_class
import logging

logger = logging.getLogger(__name__)

class CheckoutDebugView(CheckoutSessionMixin, View):
    """
    Debug the checkout session and submission building
    """
    
    def get(self, request, *args, **kwargs):
        """
        Test checkout session building
        """
        results = []
        
        try:
            results.append("=== CHECKOUT DEBUG ===")
            
            # Check if we can build submission
            try:
                # Use the correct method to build submission
                from oscar.apps.checkout.mixins import OrderPlacementMixin
                
                # Create a test view instance that has the mixin
                class TestOrderPlacement(OrderPlacementMixin, CheckoutSessionMixin):
                    def __init__(self, request):
                        self.request = request
                
                test_view = TestOrderPlacement(request)
                submission = test_view.build_submission()
                
                results.append("✅ Submission built successfully")
                results.append(f"Submission keys: {list(submission.keys())}")
                
                if 'basket' in submission:
                    basket = submission['basket']
                    results.append(f"📦 Basket ID: {basket.id}")
                    results.append(f"📦 Basket items: {basket.num_items}")
                    results.append(f"📦 Basket total: {basket.total_incl_tax}")
                    results.append(f"📦 Basket currency: {basket.currency}")
                
                if 'order_total' in submission:
                    results.append(f"💰 Order total: {submission['order_total']}")
                
                if 'user' in submission:
                    user = submission['user']
                    results.append(f"👤 User: {user}")
                
                if 'shipping_address' in submission:
                    addr = submission['shipping_address']
                    results.append(f"🏠 Shipping address: {addr.summary if addr else 'None'}")
                
                if 'billing_address' in submission:
                    addr = submission['billing_address']
                    results.append(f"🏠 Billing address: {addr.summary if addr else 'None'}")
                
                if 'shipping_method' in submission:
                    method = submission['shipping_method']
                    results.append(f"🚚 Shipping method: {method}")
                
            except Exception as e:
                results.append(f"❌ Failed to build submission: {str(e)}")
                import traceback
                results.append(f"Traceback: {traceback.format_exc()}")
            
            # Check session data
            results.append("\n=== SESSION DATA ===")
            session_keys = list(request.session.keys())
            results.append(f"Session keys: {session_keys}")
            
            for key in session_keys:
                if 'checkout' in key.lower() or 'basket' in key.lower() or 'worldpay' in key.lower():
                    results.append(f"{key}: {request.session[key]}")
            
            # Check basket in session
            if hasattr(request, 'basket'):
                results.append(f"Request basket: {request.basket}")
                results.append(f"Request basket items: {request.basket.num_items}")
            
        except Exception as e:
            results.append(f"💥 Critical error: {str(e)}")
            import traceback
            results.append(f"Traceback: {traceback.format_exc()}")
        
        html = f"""
        <h1>Checkout Debug</h1>
        <pre>{'<br>'.join(results)}</pre>
        <p><a href="/basket/">Go to Basket</a></p>
        <p><a href="/checkout/">Go to Checkout</a></p>
        """
        return HttpResponse(html)


class PaymentMethodTestView(View):
    """
    Test payment method form
    """
    
    def get(self, request, *args, **kwargs):
        """
        Test the payment method form
        """
        from payment.forms import WorldpayPaymentDetailsForm
        from django.middleware.csrf import get_token
        
        form = WorldpayPaymentDetailsForm()
        csrf_token = get_token(request)
        
        results = []
        results.append("=== PAYMENT METHOD FORM TEST ===")
        results.append(f"Form fields: {list(form.fields.keys())}")
        results.append(f"Payment choices: {form.fields['payment_method'].choices}")
        results.append(f"Initial value: {form.fields['payment_method'].initial}")
        
        # Test form rendering
        form_html = str(form)
        results.append(f"Form HTML length: {len(form_html)} characters")
        
        html = f"""
        <h1>Payment Method Form Test</h1>
        <pre>{'<br>'.join(results)}</pre>
        
        <h2>Actual Form:</h2>
        <form method="post" action="/payment/gateway/redirect/">
            <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}">
            {form}
            <button type="submit">Test Submit</button>
        </form>
        
        <p><strong>Note:</strong> This is just a visual test. Use the actual checkout flow to test payment.</p>
        <p><a href="/checkout/">Go to Checkout</a></p>
        <p><a href="/payment/debug/checkout/">Debug Checkout Session</a></p>
        """
        return HttpResponse(html)

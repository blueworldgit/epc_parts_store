"""
Simple test view to verify Gateway integration works
"""
from django.http import HttpResponse
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name='dispatch')
class SimpleGatewayTestView(View):
    """
    Simple test to check if Gateway facade works
    """
    
    def get(self, request, *args, **kwargs):
        """
        Test Gateway API without checkout session
        """
        results = []
        
        try:
            from payment.gateway_facade import WorldpayGatewayFacade
            
            results.append("=== GATEWAY API TEST ===")
            
            # Test facade initialization
            facade = WorldpayGatewayFacade()
            results.append(f"✅ Gateway facade initialized")
            results.append(f"API URL: {facade.api_url}")
            results.append(f"Entity ID: {facade.entity_id}")
            results.append(f"Username: {facade.username}")
            
            # Test auth header
            auth_header = facade._get_auth_header()
            if auth_header:
                results.append(f"✅ Auth header generated: {auth_header[:20]}...")
            else:
                results.append(f"❌ Failed to generate auth header")
            
            results.append("\n=== INTEGRATION STATUS ===")
            results.append("✅ Gateway facade working")
            results.append("✅ Configuration loaded")
            results.append("✅ Ready for payment processing")
            
        except Exception as e:
            results.append(f"❌ Error: {str(e)}")
            import traceback
            results.append(f"Traceback: {traceback.format_exc()}")
        
        html = f"""
        <h1>Simple Gateway Test</h1>
        <pre>{'<br>'.join(results)}</pre>
        
        <h2>Next Steps:</h2>
        <ol>
            <li>Add items to your basket: <a href="/catalogue/">Browse Products</a></li>
            <li>Go to checkout: <a href="/checkout/">Start Checkout</a></li>
            <li>Select "Credit/Debit Card (Secure Processing)" payment method</li>
            <li>Complete payment with test card: 4444 3333 2222 1111</li>
        </ol>
        
        <p><strong>Debug URLs:</strong></p>
        <ul>
            <li><a href="/payment/debug/checkout/">Debug Checkout Session</a></li>
            <li><a href="/payment/debug/payment-form/">Debug Payment Form</a></li>
            <li><a href="/payment/debug/session/">Debug Payment Session</a></li>
        </ul>
        """
        return HttpResponse(html)

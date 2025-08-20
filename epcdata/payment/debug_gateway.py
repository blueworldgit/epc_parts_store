"""
Debug views for payment troubleshooting
"""
import logging
from django.http import JsonResponse, HttpResponse
from django.views.generic import View
from django.shortcuts import render
from oscar.core.loading import get_model

logger = logging.getLogger(__name__)

class PaymentSessionDebugView(View):
    """
    Debug view to check payment session data
    """
    
    def get(self, request, *args, **kwargs):
        """
        Display current session data for debugging
        """
        session_data = request.session.get('worldpay_gateway_submission')
        
        debug_info = {
            'session_exists': session_data is not None,
            'session_data': session_data,
            'session_keys': list(request.session.keys()),
        }
        
        if session_data:
            submission_data = session_data.get('submission_data', {})
            
            # Check if referenced objects exist
            try:
                Basket = get_model('basket', 'Basket')
                basket = Basket.objects.get(id=submission_data.get('basket_id'))
                debug_info['basket_exists'] = True
                debug_info['basket_info'] = {
                    'id': basket.id,
                    'num_items': basket.num_items,
                    'total_incl_tax': str(basket.total_incl_tax),
                    'currency': str(basket.currency),
                }
            except Exception as e:
                debug_info['basket_exists'] = False
                debug_info['basket_error'] = str(e)
            
            # Check addresses
            if submission_data.get('shipping_address_id'):
                try:
                    from oscar.apps.address.models import UserAddress
                    addr = UserAddress.objects.get(id=submission_data['shipping_address_id'])
                    debug_info['shipping_address_exists'] = True
                    debug_info['shipping_address'] = addr.summary
                except Exception as e:
                    debug_info['shipping_address_exists'] = False
                    debug_info['shipping_address_error'] = str(e)
            
            if submission_data.get('billing_address_id'):
                try:
                    from oscar.apps.address.models import UserAddress
                    addr = UserAddress.objects.get(id=submission_data['billing_address_id'])
                    debug_info['billing_address_exists'] = True
                    debug_info['billing_address'] = addr.summary
                except Exception as e:
                    debug_info['billing_address_exists'] = False
                    debug_info['billing_address_error'] = str(e)
            
            # Check user
            if submission_data.get('user'):
                try:
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    user = User.objects.get(pk=submission_data['user'])
                    debug_info['user_exists'] = True
                    debug_info['user_info'] = str(user)
                except Exception as e:
                    debug_info['user_exists'] = False
                    debug_info['user_error'] = str(e)
        
        # Return as JSON for easy reading
        if request.GET.get('format') == 'json':
            return JsonResponse(debug_info, indent=2)
        
        # Return as HTML
        html = f"""
        <h1>Payment Session Debug</h1>
        <pre>{debug_info}</pre>
        <p><a href="?format=json">View as JSON</a></p>
        """
        return HttpResponse(html)


class PaymentTestOrderCreationView(View):
    """
    Test order creation without payment
    """
    
    def get(self, request, *args, **kwargs):
        """
        Test order creation process
        """
        session_data = request.session.get('worldpay_gateway_submission')
        
        if not session_data:
            return HttpResponse("<h1>No session data found</h1><p>Go through checkout first</p>")
        
        results = []
        
        try:
            results.append("=== ORDER CREATION TEST ===")
            
            # Generate a unique order number for testing
            import time
            unique_order_number = f"100{int(time.time() % 10000):04d}"
            
            # Update session data with unique order number
            if session_data:
                session_data['order_number'] = unique_order_number
                request.session['worldpay_gateway_submission'] = session_data
                results.append(f"✅ Updated order number to: {unique_order_number}")
            
            results.append(f"Session data: {session_data}")
            
            # Import the create order method
            from payment.gateway_views import WorldpayGatewayCardFormView
            view = WorldpayGatewayCardFormView()
            
            results.append("✅ View imported successfully")
            results.append("🔧 Testing order creation...")
            
            # Try to create order with detailed logging
            try:
                order = view._create_order_from_session(request, session_data)
                
                if order:
                    results.append(f"✅ Order created successfully: {order.number}")
                    results.append(f"Order ID: {order.id}")
                    results.append(f"Order total: {order.total_incl_tax}")
                    results.append(f"Order status: {order.status}")
                    results.append(f"Order user: {order.user}")
                else:
                    results.append("❌ Order creation returned None")
                    
            except Exception as e:
                results.append(f"💥 Exception during order creation: {str(e)}")
                results.append(f"Exception type: {type(e).__name__}")
                import traceback
                results.append(f"Full traceback:")
                results.append(traceback.format_exc())
                
        except Exception as e:
            results.append(f"💥 Critical error in test: {str(e)}")
            import traceback
            results.append(f"Traceback: {traceback.format_exc()}")
        
        # Format results properly
        formatted_results = []
        for result in results:
            if isinstance(result, str):
                # Escape HTML and preserve line breaks
                escaped = result.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                formatted_results.append(escaped)
            else:
                formatted_results.append(str(result))
        
        html = f"""
        <h1>Order Creation Test</h1>
        <pre style="white-space: pre-wrap; font-family: monospace; background: #f5f5f5; padding: 15px; border-radius: 5px;">
        {'<br>'.join(formatted_results)}
        </pre>
        <p><a href="/payment/debug/session/">Back to session debug</a></p>
        <p><a href="/payment/gateway/card-form/">Try payment form</a></p>
        """
        return HttpResponse(html)

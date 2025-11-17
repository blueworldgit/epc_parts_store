#!/usr/bin/env python
"""
Test the actual gateway payment flow to verify the fix
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from decimal import Decimal
from oscar.core.loading import get_model
from oscar.core import prices
from oscar.apps.shipping.methods import FixedPrice
from django.test import RequestFactory
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.auth.models import AnonymousUser
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_gateway_order_creation():
    """Test the actual gateway view order creation"""
    
    print("🧪 Testing Gateway Order Creation Flow")
    print("=" * 50)
    
    try:
        # Import the actual gateway view
        from payment.gateway_views import WorldpayGatewayCardFormView
        
        # Get models
        User = get_model('auth', 'User')
        Basket = get_model('basket', 'Basket')
        Product = get_model('catalogue', 'Product')
        Order = get_model('order', 'Order')
        
        # Get a test user (create one if needed)
        user, created = User.objects.get_or_create(
            email='test@example.com',
            defaults={'username': 'testuser', 'first_name': 'Test', 'last_name': 'User'}
        )
        print(f"✅ Using test user: {user.email}")
        
        # Create a test basket with products and strategy
        basket = Basket.objects.create(owner=user)
        
        # Assign strategy to basket
        from oscar.core.loading import get_class
        try:
            DefaultStrategy = get_class('partner.strategy', 'Default')
            strategy = DefaultStrategy()
            basket.strategy = strategy
            print(f"✅ Strategy assigned to basket: {strategy}")
        except Exception as strategy_error:
            print(f"⚠️ Could not get Default strategy: {strategy_error}")
            from oscar.apps.partner.strategy import Default as FallbackStrategy
            strategy = FallbackStrategy()
            basket.strategy = strategy
            print(f"✅ Fallback strategy assigned to basket: {strategy}")
        
        # Add a product to basket
        products = Product.objects.all()[:1]
        if products:
            product = products[0]
            basket.add_product(product, quantity=1)
            print(f"🛒 Added product to basket: {product.title}")
            print(f"💰 Basket total: £{basket.total_incl_tax}")
        else:
            print("❌ No products found in database")
            return
        
        # Create mock session data like the checkout would
        session_data = {
            'order_number': 'TEST-GATEWAY-001',
            'order_total': str(basket.total_incl_tax + Decimal('11.95')),  # Add shipping
            'submission_data': {
                'basket_id': basket.id,
                'user': user.id,
                'shipping_method_code': 'weight_based',
                'shipping_charge': '11.95',
                'shipping_address_id': None,
                'billing_address_id': None,
            }
        }
        
        print(f"📝 Session data created: {session_data}")
        
        # Create a mock request
        factory = RequestFactory()
        request = factory.post('/payment/gateway/card-form/')
        request.user = user
        request.session = SessionStore()
        request.session['gateway_payment_data'] = session_data
        request.session.save()
        
        # Create view instance
        view = WorldpayGatewayCardFormView()
        
        # Test the order creation method directly
        print("\n🔨 Testing _create_order_from_session method...")
        
        try:
            order = view._create_order_from_session(request, session_data)
            
            if order:
                print(f"✅ Order created successfully: {order.number}")
                print(f"💰 Order total: £{order.total_incl_tax}")
                print(f"🚚 Order shipping: £{getattr(order, 'shipping_incl_tax', 'N/A')}")
                
                # Clean up
                order.delete()
                print("🗑️ Cleaned up test order")
            else:
                print("❌ Order creation returned None")
                
        except Exception as e:
            print(f"❌ Order creation failed: {e}")
            print(f"Exception type: {type(e).__name__}")
            import traceback
            print("📋 Full traceback:")
            traceback.print_exc()
        
        # Clean up basket
        basket.delete()
        
        print("\n✅ Gateway order creation test completed")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_gateway_order_creation()
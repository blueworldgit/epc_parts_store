#!/usr/bin/env python
"""
Simple test for order creation debugging
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from decimal import Decimal
from oscar.core.loading import get_model
from oscar.apps.order.utils import OrderCreator
from oscar.core import prices
from oscar.apps.shipping.methods import FixedPrice
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_order_creation():
    """Test order creation with shipping to find the issue"""
    
    print("🧪 Testing Order Creation")
    print("=" * 50)
    
    try:
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
        
        # Create a test basket with products
        basket = Basket.objects.create(owner=user)
        
        # CRITICAL: Assign strategy to basket
        from oscar.core.loading import get_class
        try:
            DefaultStrategy = get_class('partner.strategy', 'Default')
            strategy = DefaultStrategy()
            basket.strategy = strategy
            print(f"✅ Strategy assigned to basket: {strategy}")
        except Exception as strategy_error:
            print(f"⚠️ Could not get Default strategy: {strategy_error}")
            # Fallback: create a minimal strategy manually
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
        else:
            print("❌ No products found in database")
            return
        
        # Create shipping method
        shipping_charge = Decimal('11.95')
        shipping_method = FixedPrice(charge_excl_tax=shipping_charge, charge_incl_tax=shipping_charge)
        shipping_method.code = 'weight_based'
        shipping_method.name = 'Standard Shipping'
        shipping_method.description = 'Weight-based shipping'
        
        # Create shipping total (Price object)
        shipping_total = prices.Price(
            currency=basket.currency,
            excl_tax=shipping_charge,
            incl_tax=shipping_charge
        )
        
        print(f"🚚 Shipping method: {shipping_method.name} - £{shipping_charge}")
        print(f"🏷️ Shipping total type: {type(shipping_total)}")
        
        # Create order total
        order_total = prices.Price(
            currency=basket.currency,
            excl_tax=basket.total_excl_tax + shipping_charge,
            incl_tax=basket.total_incl_tax + shipping_charge
        )
        
        print(f"💰 Order total: £{order_total.incl_tax}")
        
        # Test OrderCreator approach - exact same call as gateway_views.py
        try:
            print("\n🔨 Testing OrderCreator approach...")
            order_creator = OrderCreator()
            
            # This is the EXACT call from gateway_views.py line 557-565
            order = order_creator.place_order(
                basket=basket,
                total=order_total,
                shipping_method=shipping_method,
                shipping_charge=shipping_total,  # This was missing!
                user=user,
                order_number='TEST-ORDER-001'
            )
            
            print(f"✅ OrderCreator succeeded: {order.number}")
            print(f"📦 Order shipping: £{getattr(order, 'shipping_incl_tax', 'N/A')}")
            
            # Clean up
            order.delete()
            
        except Exception as e:
            print(f"❌ OrderCreator failed: {e}")
            print(f"Exception type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            
            # Check OrderCreator method signature
            print("\n🔍 Checking OrderCreator.place_order signature...")
            import inspect
            sig = inspect.signature(order_creator.place_order)
            print(f"Method signature: {sig}")
        
        # Clean up basket
        basket.delete()
        
        print("\n✅ Order creation test completed")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_order_creation()
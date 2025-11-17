#!/usr/bin/env python
"""
Test order creation to debug the payment gateway issue
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
        
        shipping_total = prices.Price(
            currency=basket.currency,
            excl_tax=shipping_charge,
            incl_tax=shipping_charge
        )
        
        print(f"🚚 Shipping method: {shipping_method.name} - £{shipping_charge}")
        
        # Create order total
        order_total = prices.Price(
            currency=basket.currency,
            excl_tax=basket.total_excl_tax + shipping_charge,
            incl_tax=basket.total_incl_tax + shipping_charge
        )
        
        print(f"💰 Order total: £{order_total.incl_tax}")
        
        # Test OrderCreator approach
        try:
            print("\\n🔨 Testing OrderCreator approach...")
            order_creator = OrderCreator()
            
            # Test the exact call from gateway_views.py
            order = order_creator.place_order(
                basket=basket,
                total=order_total,
                shipping_method=shipping_method,
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
            
            # Test direct order creation
            try:
                print("\\n🔄 Testing direct Order creation...")
                
                # Check what fields Order model has
                field_names = [f.name for f in Order._meta.get_fields()]
                print(f"📋 Order model fields: {', '.join(sorted(field_names))}")
                
                # Create order data
                order_data = {
                    'number': 'TEST-DIRECT-001',
                    'user': user,
                    'total_incl_tax': basket.total_incl_tax + shipping_charge,
                    'total_excl_tax': basket.total_excl_tax + shipping_charge,
                    'currency': basket.currency,
                    'status': 'Pending'
                }
                
                # Add shipping fields if they exist
                if 'shipping_incl_tax' in field_names:
                    order_data['shipping_incl_tax'] = shipping_charge
                if 'shipping_excl_tax' in field_names:
                    order_data['shipping_excl_tax'] = shipping_charge
                if 'shipping_method' in field_names:
                    order_data['shipping_method'] = shipping_method.name
                
                order = Order.objects.create(**order_data)
                
                print(f"✅ Direct creation succeeded: {order.number}")
                print(f"💰 Order total: £{order.total_incl_tax}")
                print(f"🚚 Order shipping: £{getattr(order, 'shipping_incl_tax', 'N/A')}")
                
                # Clean up
                order.delete()
                
            except Exception as e2:
                print(f"❌ Direct creation failed: {e2}")
                import traceback
                traceback.print_exc()
        
        # Clean up basket
        basket.delete()
        
        print("\\n✅ Order creation test completed")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_order_creation()
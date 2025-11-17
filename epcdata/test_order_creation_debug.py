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
        )\n        \n        print(f\"🚚 Shipping method: {shipping_method.name} - £{shipping_charge}\")\n        \n        # Create order total\n        order_total = prices.Price(\n            currency=basket.currency,\n            excl_tax=basket.total_excl_tax + shipping_charge,\n            incl_tax=basket.total_incl_tax + shipping_charge\n        )\n        \n        print(f\"💰 Order total: £{order_total.incl_tax}\")\n        \n        # Test OrderCreator approach\n        try:\n            print(\"\\n🔨 Testing OrderCreator approach...\")\n            order_creator = OrderCreator()\n            \n            # Test the exact call from gateway_views.py\n            order = order_creator.place_order(\n                basket=basket,\n                total=order_total,\n                shipping_method=shipping_method,\n                user=user,\n                order_number='TEST-ORDER-001'\n            )\n            \n            print(f\"✅ OrderCreator succeeded: {order.number}\")\n            print(f\"📦 Order shipping: £{getattr(order, 'shipping_incl_tax', 'N/A')}\")\n            \n            # Clean up\n            order.delete()\n            \n        except Exception as e:\n            print(f\"❌ OrderCreator failed: {e}\")\n            print(f\"Exception type: {type(e).__name__}\")\n            import traceback\n            traceback.print_exc()\n            \n            # Test direct order creation\n            try:\n                print(\"\\n🔄 Testing direct Order creation...\")\n                \n                # Check what fields Order model has\n                field_names = [f.name for f in Order._meta.get_fields()]\n                print(f\"📋 Order model fields: {', '.join(sorted(field_names))}\")\n                \n                # Create order data\n                order_data = {\n                    'number': 'TEST-DIRECT-001',\n                    'user': user,\n                    'total_incl_tax': basket.total_incl_tax + shipping_charge,\n                    'total_excl_tax': basket.total_excl_tax + shipping_charge,\n                    'currency': basket.currency,\n                    'status': 'Pending'\n                }\n                \n                # Add shipping fields if they exist\n                if 'shipping_incl_tax' in field_names:\n                    order_data['shipping_incl_tax'] = shipping_charge\n                if 'shipping_excl_tax' in field_names:\n                    order_data['shipping_excl_tax'] = shipping_charge\n                if 'shipping_method' in field_names:\n                    order_data['shipping_method'] = shipping_method.name\n                \n                order = Order.objects.create(**order_data)\n                \n                print(f\"✅ Direct creation succeeded: {order.number}\")\n                print(f\"💰 Order total: £{order.total_incl_tax}\")\n                print(f\"🚚 Order shipping: £{getattr(order, 'shipping_incl_tax', 'N/A')}\")\n                \n                # Clean up\n                order.delete()\n                \n            except Exception as e2:\n                print(f\"❌ Direct creation failed: {e2}\")\n                import traceback\n                traceback.print_exc()\n        \n        # Clean up basket\n        basket.delete()\n        \n        print(\"\\n✅ Order creation test completed\")\n        \n    except Exception as e:\n        print(f\"❌ Test failed: {e}\")\n        import traceback\n        traceback.print_exc()\n\nif __name__ == \"__main__\":\n    test_order_creation()
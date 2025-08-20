#!/usr/bin/env python
"""
Test order creation with proper debugging
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

def test_order_creation():
    print("🧪 Testing Order Creation...")
    
    try:
        # Import required models
        from oscar.apps.basket.models import Basket
        from oscar.core.loading import get_model, get_class
        from django.contrib.auth import get_user_model
        from oscar.apps.shipping.methods import FixedPrice
        from oscar.apps.order.models import ShippingAddress, BillingAddress
        from oscar.apps.address.models import Country
        from oscar.apps.order.utils import OrderCreator
        from decimal import Decimal
        import time
        
        User = get_user_model()
        
        print("✅ All imports successful")
        
        # Get test basket
        baskets = Basket.objects.filter(lines__isnull=False).distinct()
        basket = None
        for b in baskets:
            if b.num_items > 0:
                basket = b
                break
        
        if not basket:
            print("❌ No basket with items found")
            return
            
        print(f"✅ Found basket {basket.id} with {basket.num_items} items")
        
        # Assign strategy to basket
        DefaultStrategy = get_class('partner.strategy', 'Default')
        strategy = DefaultStrategy()
        basket.strategy = strategy
        print(f"✅ Strategy assigned: {basket.total_incl_tax}")
        
        # Get user
        user = User.objects.first()
        print(f"✅ Found user: {user}")
        
        # Create shipping method
        shipping_method = FixedPrice(charge_excl_tax=Decimal('0.00'), charge_incl_tax=Decimal('0.00'))
        print(f"✅ Created shipping method: {shipping_method}")
        print(f"   Shipping method type: {type(shipping_method)}")
        print(f"   Shipping method attrs: {[attr for attr in dir(shipping_method) if not attr.startswith('_')]}")
        
        # Test shipping charge calculation
        if hasattr(shipping_method, 'calculate'):
            shipping_total = shipping_method.calculate(basket)
            print(f"✅ Using calculate(): {shipping_total}")
            print(f"   Shipping total type: {type(shipping_total)}")
        elif hasattr(shipping_method, 'charge_incl_tax'):
            shipping_charge = shipping_method.charge_incl_tax
            print(f"✅ Using charge_incl_tax: {shipping_charge}")
            # Create shipping charge as Money object
            from oscar.core import prices
            shipping_total = prices.Price(
                currency=basket.currency,
                excl_tax=shipping_charge,
                incl_tax=shipping_charge
            )
        else:
            shipping_charge = Decimal('0.00')
            print(f"✅ Fallback shipping charge: {shipping_charge}")
            # Create shipping charge as Money object
            from oscar.core import prices
            shipping_total = prices.Price(
                currency=basket.currency,
                excl_tax=shipping_charge,
                incl_tax=shipping_charge
            )
        
        # Create addresses
        country = Country.objects.get(iso_3166_1_a2='GB')  # UK
        
        shipping_address = ShippingAddress(
            first_name='Test',
            last_name='User',
            line1='123 Test Street',
            line4='Test City',
            postcode='TE5T 1NG',
            country=country
        )
        shipping_address.save()
        print(f"✅ Created shipping address: {shipping_address.id}")
        
        billing_address = BillingAddress(
            first_name='Test',
            last_name='User',
            line1='123 Test Street',
            line4='Test City',
            postcode='TE5T 1NG',
            country=country
        )
        billing_address.save()
        print(f"✅ Created billing address: {billing_address.id}")
        
        # Create unique order number
        order_number = f"TEST{int(time.time() % 10000):04d}"
        print(f"✅ Order number: {order_number}")
        
        # Check basket total type
        print(f"✅ Basket total type: {type(basket.total_incl_tax)}")
        print(f"✅ Basket total value: {basket.total_incl_tax}")
        print(f"✅ Basket currency: {basket.currency}")
        
        # Create Money object for total
        from oscar.core import prices
        order_total = prices.Price(
            currency=basket.currency,
            excl_tax=basket.total_excl_tax,
            incl_tax=basket.total_incl_tax
        )
        print(f"✅ Created Price object: {order_total}")
        print(f"   Price type: {type(order_total)}")
        print(f"   Price currency: {order_total.currency}")
        
        # Test order creation
        print("\n🔧 Testing order creation...")
        order_creator = OrderCreator()
        
        order = order_creator.place_order(
            basket=basket,
            total=order_total,
            shipping_method=shipping_method,
            shipping_charge=shipping_total,
            shipping_address=shipping_address,
            billing_address=billing_address,
            user=user,
            order_number=order_number
        )
        
        print(f"🎉 SUCCESS! Order created: {order.number}")
        print(f"   Order ID: {order.id}")
        print(f"   Order total: {order.total_incl_tax}")
        print(f"   Order status: {order.status}")
        
    except Exception as e:
        print(f"💥 Error: {e}")
        import traceback
        print(f"Traceback:\n{traceback.format_exc()}")

if __name__ == "__main__":
    test_order_creation()

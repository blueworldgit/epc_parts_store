#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from oscar.apps.order.models import Order

print("🔍 INVESTIGATING SHIPPING ADDRESS DIFFERENCES")
print("=" * 60)

# Compare the addresses between your working order and JASON PINK's problematic orders
orders_to_check = ['100001-9108', '100004-8138', '100004-9856']

for order_num in orders_to_check:
    try:
        order = Order.objects.get(number=order_num)
        print(f"\n📋 Order: {order.number}")
        print(f"   👤 Email: {order.user.email if order.user else order.guest_email}")
        print(f"   📅 Date: {order.date_placed}")
        
        # Check shipping address
        if order.shipping_address:
            print(f"   🏠 Shipping Address:")
            print(f"      Name: {order.shipping_address.first_name} {order.shipping_address.last_name}")
            print(f"      Line 1: {order.shipping_address.line1}")
            print(f"      Line 2: {order.shipping_address.line2}")
            print(f"      City: {order.shipping_address.line4}")
            print(f"      Postcode: {order.shipping_address.postcode}")
            print(f"      Country: {order.shipping_address.country}")
        else:
            print(f"   🏠 No shipping address")
            
        # Check billing address
        if order.billing_address:
            print(f"   💳 Billing Address:")
            print(f"      Name: {order.billing_address.first_name} {order.billing_address.last_name}")
            print(f"      Line 1: {order.billing_address.line1}")
            print(f"      Line 2: {order.billing_address.line2}")
            print(f"      City: {order.billing_address.line4}")
            print(f"      Postcode: {order.billing_address.postcode}")
            print(f"      Country: {order.billing_address.country}")
        else:
            print(f"   💳 No billing address")
            
    except Order.DoesNotExist:
        print(f"\n❌ Order {order_num} not found")

print(f"\n🔍 KEY THINGS TO CHECK:")
print(f"   1. Do different addresses cause different API request structures?")
print(f"   2. Are there country code validation issues?")
print(f"   3. Do special characters in addresses cause JSON parsing problems?")
print(f"   4. Are there postcode format validation differences?")
print(f"   5. Does address verification affect payment response parsing?")

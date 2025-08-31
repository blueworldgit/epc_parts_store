#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from oscar.apps.order.models import Order

# Check both orders
orders = ['100001-9108', '100004-8138']

for order_num in orders:
    try:
        order = Order.objects.get(number=order_num)
        print(f'\n📋 Order: {order.number}')
        print(f'   📅 Date: {order.date_placed}')
        print(f'   💰 Total: £{order.total_incl_tax}')
        print(f'   📊 Status: "{order.status}"')
        print(f'   👤 Email: {order.user.email if order.user else order.guest_email}')
        
        # Check if there's any difference in order completion
        print(f'   🏁 Order complete: {order.status == "Complete" or order.status == ""}')
        
    except Order.DoesNotExist:
        print(f'\n❌ Order {order_num} not found')

# Let's also check what the actual redirect difference might be
print(f'\n💡 KEY INSIGHT:')
print(f'   Both orders have NO payment sources')
print(f'   Both payments were processed by Worldpay')
print(f'   The difference must be in the session/redirect handling')
print(f'   Working order showed success page')
print(f'   Problem order redirected to product page')

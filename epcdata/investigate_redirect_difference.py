#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from oscar.apps.order.models import Order
from django.contrib.sessions.models import Session

print("🔍 INVESTIGATING REDIRECT BEHAVIOR DIFFERENCES")
print("=" * 60)

# Check both orders
orders = ['100001-9108', '100004-8138']

for order_num in orders:
    try:
        order = Order.objects.get(number=order_num)
        print(f'\n📋 Order: {order.number}')
        print(f'   📅 Date: {order.date_placed}')
        print(f'   👤 Email: {order.user.email if order.user else order.guest_email}')
        print(f'   🌐 User Agent Info: {order.user if order.user else "Guest"}')
        
        # Time difference
        from datetime import datetime
        import pytz
        now = datetime.now(pytz.UTC)
        time_diff = now - order.date_placed
        print(f'   ⏰ Time since order: {time_diff.total_seconds()/60:.1f} minutes ago')
        
    except Order.DoesNotExist:
        print(f'\n❌ Order {order_num} not found')

print(f'\n💡 POSSIBLE CAUSES FOR REDIRECT DIFFERENCES:')
print(f'   1. Session timeout/expiry between orders')
print(f'   2. Browser cache differences') 
print(f'   3. Different error handling paths in code')
print(f'   4. User agent or browser differences')
print(f'   5. Race conditions in session handling')

print(f'\n🔍 THEORY:')
print(f'   Working order (100001-9108): Recent, fresh session')
print(f'   Problem order (100004-8138): Earlier, possibly stale session')
print(f'   The JSON parsing fix probably resolved the core issue')
print(f'   But order 100004-8138 was before the fix was deployed')

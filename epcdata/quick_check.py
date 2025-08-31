#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from oscar.apps.order.models import Order

print("Looking for order 100004-9856...")

try:
    orders = Order.objects.filter(number='100004-9856')
    print(f"Found {orders.count()} orders")
    
    for order in orders:
        print(f"Order: {order.number}")
        print(f"Date: {order.date_placed}")
        print(f"Total: £{order.total_incl_tax}")
        print(f"Status: '{order.status}'")
        print(f"Email: {order.user.email if order.user else order.guest_email}")
        
        # Check payment sources
        sources = order.sources.all()
        print(f"Payment sources: {sources.count()}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

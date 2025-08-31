#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from oscar.apps.order.models import Order

print("🔍 COMPARING SESSION DATA CLUES BETWEEN WORKING vs PROBLEMATIC ORDERS")
print("=" * 80)

# Compare the key differences between your working order and JASON PINK's failing orders
orders_to_compare = [
    ('100001-9108', 'YOUR CARD - WORKED (showed thank-you)'),
    ('100004-1610', 'JASON PINK - FAILED (redirected)')
]

for order_num, description in orders_to_compare:
    try:
        order = Order.objects.get(number=order_num)
        print(f"\n📋 {description}")
        print(f"   Order: {order.number}")
        print(f"   Date: {order.date_placed}")
        print(f"   Email: {order.user.email if order.user else order.guest_email}")
        print(f"   User ID: {order.user.id if order.user else 'Guest'}")
        print(f"   Payment Sources: {order.sources.count()}")
        
        # Check if there are subtle differences
        if order.user:
            print(f"   User Type: Registered ({order.user.username if hasattr(order.user, 'username') else 'N/A'})")
        else:
            print(f"   User Type: Guest")
            
        # Check order timing - could session expire between payment and thank-you?
        import datetime
        now = datetime.datetime.now(order.date_placed.tzinfo)
        time_diff = now - order.date_placed
        print(f"   Time since order: {time_diff.total_seconds()/60:.1f} minutes")
        
    except Order.DoesNotExist:
        print(f"\n❌ Order {order_num} not found")

print(f"\n🔍 HYPOTHESIS - SESSION STATE DIFFERENCES:")
print(f"   1. Different users might have different session handling")
print(f"   2. Guest vs registered user checkout flow differences") 
print(f"   3. Session timeout between payment and thank-you redirect")
print(f"   4. User-specific session keys or checkout state")

print(f"\n💡 KEY INSIGHT:")
print(f"   Both orders have payment sources, so payment processing works")
print(f"   The difference is in POST-payment session state when accessing thank-you")
print(f"   Need to check what session data Oscar's ThankYouView requires")

print(f"\n🎯 NEXT INVESTIGATION:")
print(f"   Check if session checkout data persists differently for different users")
print(f"   Look at Django session table to see active sessions")
print(f"   Compare session expiry and checkout state between users")

#!/usr/bin/env python3
"""
Investigate specific order 100004-8138 that processed payment but didn't show completion
"""
import os
import django
import sys

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from oscar.apps.order.models import Order
from oscar.apps.payment.models import PaymentEvent, PaymentEventType
from oscar.apps.basket.models import Basket

def investigate_order():
    order_number = "100004-8138"
    
    print(f"=== Investigating Order {order_number} ===")
    
    try:
        # Find the order
        order = Order.objects.get(number=order_number)
        print(f"✅ Order found: {order.number}")
        print(f"Status: {order.status}")
        print(f"Total: £{order.total_incl_tax}")
        print(f"User: {order.user.email if order.user else 'Guest'}")
        print(f"Created: {order.date_placed}")
        
        print("\n--- Shipping Address ---")
        if order.shipping_address:
            addr = order.shipping_address
            print(f"Name: {addr.first_name} {addr.last_name}")
            print(f"Line1: {addr.line1}")
            print(f"Line2: {addr.line2 or 'N/A'}")
            print(f"Line3: {addr.line3 or 'N/A'}")
            print(f"City: {addr.line4}")
            print(f"Postcode: {addr.postcode}")
            print(f"Country: {addr.country}")
            print(f"Phone: {addr.phone_number or 'N/A'}")
            
            # Check for potential problematic characters
            problematic_fields = []
            for field_name, value in [
                ('first_name', addr.first_name),
                ('last_name', addr.last_name),
                ('line1', addr.line1),
                ('line2', addr.line2),
                ('line3', addr.line3),
                ('line4', addr.line4),
                ('postcode', addr.postcode)
            ]:
                if value and any(ord(char) > 127 for char in str(value)):
                    problematic_fields.append(f"{field_name}: {value}")
            
            if problematic_fields:
                print(f"⚠️  Non-ASCII characters found:")
                for field in problematic_fields:
                    print(f"   {field}")
        else:
            print("❌ No shipping address found")
        
        print("\n--- Billing Address ---")
        if order.billing_address:
            addr = order.billing_address
            print(f"Name: {addr.first_name} {addr.last_name}")
            print(f"Line1: {addr.line1}")
            print(f"City: {addr.line4}")
            print(f"Postcode: {addr.postcode}")
            print(f"Country: {addr.country}")
        else:
            print("❌ No billing address found")
        
        print("\n--- Payment Events ---")
        payment_events = PaymentEvent.objects.filter(order=order).order_by('date_created')
        if payment_events:
            for event in payment_events:
                print(f"Event: {event.event_type.name}")
                print(f"  Amount: £{event.amount}")
                print(f"  Reference: {event.reference}")
                print(f"  Date: {event.date_created}")
                print(f"  Lines: {event.lines.count()}")
                print("---")
        else:
            print("❌ No payment events found")
        
        print("\n--- Order Lines ---")
        for line in order.lines.all():
            print(f"Product: {line.product.title}")
            print(f"  Quantity: {line.quantity}")
            print(f"  Price: £{line.line_price_incl_tax}")
            print(f"  Status: {line.status}")
        
        # Check for any issues with the order completion
        print("\n--- Order Completion Analysis ---")
        if order.status == 'Complete':
            print("✅ Order status is Complete")
        else:
            print(f"⚠️  Order status is '{order.status}' (not Complete)")
        
        # Check payment authorization
        auth_events = payment_events.filter(event_type__name='Authorised')
        if auth_events:
            print(f"✅ Found {auth_events.count()} authorization event(s)")
        else:
            print("❌ No authorization events found")
        
        # Check if there's a basket associated
        print(f"\n--- Additional Details ---")
        print(f"Order ID: {order.id}")
        print(f"Guest email: {order.guest_email or 'N/A'}")
        
    except Order.DoesNotExist:
        print(f"❌ Order {order_number} not found in database")
    except Exception as e:
        print(f"❌ Error investigating order: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    investigate_order()

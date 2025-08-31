#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from oscar.apps.order.models import Order
from oscar.apps.payment.models import SourceType, Source, Transaction

def investigate_order(order_number):
    print(f"Investigating Order: {order_number}")
    print("=" * 50)
    
    try:
        order = Order.objects.get(number=order_number)
        print(f"Order Status: {order.status}")
        print(f"Date Placed: {order.date_placed}")
        print(f"Total: £{order.total_incl_tax}")
        print(f"Currency: {order.currency}")
        
        # Check if order has a user or is guest
        if order.user:
            print(f"User: {order.user.username} ({order.user.email})")
        else:
            print(f"Guest Email: {order.guest_email}")
        
        # Check shipping address
        shipping_address = order.shipping_address
        if shipping_address:
            print(f"Shipping Address:")
            print(f"  Name: {shipping_address.first_name} {shipping_address.last_name}")
            print(f"  Line 1: {shipping_address.line1}")
            if shipping_address.line2:
                print(f"  Line 2: {shipping_address.line2}")
            print(f"  City: {shipping_address.line4}")
            print(f"  Postcode: {shipping_address.postcode}")
            print(f"  Country: {shipping_address.country}")
        
        # Check billing address
        billing_address = order.billing_address
        if billing_address:
            print(f"Billing Address:")
            print(f"  Name: {billing_address.first_name} {billing_address.last_name}")
            print(f"  Line 1: {billing_address.line1}")
            if billing_address.line2:
                print(f"  Line 2: {billing_address.line2}")
            print(f"  City: {billing_address.line4}")
            print(f"  Postcode: {billing_address.postcode}")
            print(f"  Country: {billing_address.country}")
        
        # Check order lines
        print(f"Order Lines ({order.lines.count()}):")
        for line in order.lines.all():
            print(f"  - {line.product.title}: Qty {line.quantity} @ £{line.unit_price_incl_tax}")
        
        # Check payment sources
        payment_sources = Source.objects.filter(order=order)
        if payment_sources:
            print(f"Payment Sources ({payment_sources.count()}):")
            for source in payment_sources:
                print(f"  - {source.source_type.name}: £{source.amount_allocated}")
                print(f"    Reference: {source.reference}")
                
                # Check transactions for this source
                transactions = Transaction.objects.filter(source=source)
                print(f"    Transactions ({transactions.count()}):")
                for txn in transactions:
                    print(f"      {txn.txn_type}: £{txn.amount} - {txn.status}")
                    print(f"       Date: {txn.date_created}")
        else:
            print("No payment sources found")

    except Order.DoesNotExist:
        print(f"Order {order_number} not found")
        # Search for similar orders
        similar_orders = Order.objects.filter(number__icontains='100004').order_by('-date_placed')[:5]
        if similar_orders:
            print("Recent similar orders:")
            for order in similar_orders:
                print(f"  {order.number} - {order.date_placed} - £{order.total_incl_tax} - {order.status}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    investigate_order("100004-8138")

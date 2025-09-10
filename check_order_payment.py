#!/usr/bin/env python
"""
Quick script to check order #100001-3033 payment details
"""
import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'epcdata'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')

django.setup()

from oscar.core.loading import get_model

def check_order():
    Order = get_model('order', 'Order')
    Source = get_model('payment', 'Source')
    Transaction = get_model('payment', 'Transaction')
    
    try:
        order = Order.objects.get(number='100003-4608')
        print(f"Order: {order.number}")
        print(f"Status: '{order.status}'")
        print(f"Total: {order.total_incl_tax}")
        print(f"User: {order.user}")
        print(f"Email: {order.email}")
        print(f"Date created: {order.date_placed}")
        
        # Check payment sources
        sources = order.sources.all()
        print(f"\nPayment Sources: {len(sources)}")
        for source in sources:
            print(f"  - Source: {source.source_type.name}, Amount: {source.amount_debited}, Ref: {source.reference}")
            
        # Check transactions
        transactions = Transaction.objects.filter(source__in=sources)
        print(f"\nTransactions: {len(transactions)}")
        for txn in transactions:
            print(f"  - Type: {txn.txn_type}, Amount: {txn.amount}, Status: {txn.status}, Ref: {txn.reference}")
            
    except Order.DoesNotExist:
        print("Order #100003-3550 not found")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    check_order()

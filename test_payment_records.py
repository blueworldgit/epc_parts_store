#!/usr/bin/env python
"""
Test payment records creation to isolate the exact issue
"""
import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'epcdata'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')

django.setup()

from oscar.core.loading import get_model
from decimal import Decimal

def test_payment_records_creation():
    """Test creating payment records for an existing order"""
    Order = get_model('order', 'Order')
    Source = get_model('payment', 'Source')
    SourceType = get_model('payment', 'SourceType')
    Transaction = get_model('payment', 'Transaction')
    
    try:
        # Get the latest failed order
        order = Order.objects.get(number='100003-3550')
        print(f"Testing payment records creation for order: {order.number}")
        print(f"Current status: '{order.status}'")
        print(f"Total: {order.total_incl_tax}")
        
        transaction_ref = f"TEST-{order.number}"
        
        print("\\n🔍 Step 1: Creating SourceType...")
        source_type, created = SourceType.objects.get_or_create(
            name='Worldpay Gateway',
            code='worldpay-gateway'
        )
        print(f"✅ SourceType {'created' if created else 'found'}: {source_type}")
        
        print("\\n🔍 Step 2: Creating Source...")
        source = Source(
            source_type=source_type,
            currency=order.currency,
            amount_allocated=order.total_incl_tax,
            amount_debited=order.total_incl_tax,
            reference=transaction_ref
        )
        source.save()
        print(f"✅ Source created with ID: {source.id}")
        
        print("\\n🔍 Step 3: Linking source to order...")
        order.sources.add(source)
        print(f"✅ Source linked to order")
        
        print("\\n🔍 Step 4: Setting order status...")
        # Check available statuses first
        try:
            order.set_status('Paid')
            print(f"✅ Order status set to: {order.status}")
        except Exception as status_error:
            print(f"❌ Error setting status: {status_error}")
            print("Trying 'Complete' status instead...")
            try:
                order.set_status('Complete')
                print(f"✅ Order status set to: {order.status}")
            except Exception as status_error2:
                print(f"❌ Error setting Complete status: {status_error2}")
        
        print("\\n🔍 Step 5: Creating transaction...")
        transaction = Transaction(
            source=source,
            txn_type=Transaction.PURCHASE,
            amount=order.total_incl_tax,
            reference='TEST-PAYMENT-ID',
            status=Transaction.COMPLETE
        )
        transaction.save()
        print(f"✅ Transaction created with ID: {transaction.id}")
        
        print("\\n🎉 All steps completed successfully!")
        print(f"Order {order.number} now has:")
        print(f"  - Status: '{order.status}'")
        print(f"  - Payment sources: {order.sources.count()}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")

if __name__ == '__main__':
    test_payment_records_creation()

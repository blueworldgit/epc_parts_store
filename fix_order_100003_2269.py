#!/usr/bin/env python
"""
Fix order #100003-2269 - add payment source and update status
"""
import os
import sys
import django
from decimal import Decimal

# Setup Django environment  
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'epcdata'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from oscar.core.loading import get_model

def fix_order():
    """Fix the specific order that's missing payment info"""
    
    Order = get_model('order', 'Order')
    Source = get_model('payment', 'Source')
    SourceType = get_model('payment', 'SourceType')
    Transaction = get_model('payment', 'Transaction')
    
    try:
        # Get the order
        order = Order.objects.get(number='100003-2269')
        print(f"Found order: {order.number}")
        print(f"Current status: '{order.status}'")
        print(f"User email: {order.email}")
        print(f"Total: £{order.total_incl_tax}")
        
        # Create payment source type if it doesn't exist
        source_type, created = SourceType.objects.get_or_create(
            name='Worldpay Gateway',
            code='worldpay-gateway'
        )
        print(f"Payment source type: {source_type.name} ({'created' if created else 'existing'})")
        
        # Create payment source
        source = Source(
            source_type=source_type,
            currency=order.currency,
            amount_allocated=order.total_incl_tax,
            amount_debited=order.total_incl_tax,
            reference=f"MANUAL-FIX-{order.number}"
        )
        source.save()
        print(f"Created payment source: {source.reference}")
        
        # Link to order
        order.sources.add(source)
        print("Linked payment source to order")
        
        # Create transaction
        transaction = Transaction(
            source=source,
            txn_type=Transaction.PURCHASE,
            amount=order.total_incl_tax,
            reference=f"MANUAL-FIX-TXN-{order.number}",
            status=Transaction.COMPLETE
        )
        transaction.save()
        print(f"Created transaction: {transaction.reference}")
        
        # Update order status
        order.set_status('Paid')
        print("Updated order status to 'Paid'")
        
        # Trigger order placed signal for email
        from oscar.apps.order.signals import order_placed
        order_placed.send(sender=None, order=order, user=order.user)
        print("Triggered order placed signal for email")
        
        print(f"\n✅ Successfully fixed order {order.number}")
        
        # Verify the fix
        updated_order = Order.objects.get(number='100003-2269')
        sources = updated_order.sources.all()
        print(f"\nVerification:")
        print(f"- Order status: '{updated_order.status}'")
        print(f"- Payment sources: {len(sources)}")
        for source in sources:
            print(f"  - {source.source_type.name}: £{source.amount_debited}")
        
        return True
        
    except Order.DoesNotExist:
        print("❌ Order not found")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    print("🔧 Fixing Order #100003-2269")
    print("=" * 40)
    success = fix_order()
    if success:
        print("\n🎉 Order fix completed successfully!")
    else:
        print("\n💥 Order fix failed!")

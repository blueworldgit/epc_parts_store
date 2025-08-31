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
from decimal import Decimal

def fix_missing_payment_source(order_number):
    """
    Add missing payment source for order that was paid but not properly linked
    """
    print(f"Fixing missing payment source for order: {order_number}")
    print("=" * 60)
    
    try:
        order = Order.objects.get(number=order_number)
        print(f"✅ Found order: {order.number}")
        print(f"Order status: {order.status}")
        print(f"Order total: £{order.total_incl_tax}")
        
        # Check existing payment sources
        existing_sources = Source.objects.filter(order=order)
        if existing_sources.exists():
            print(f"⚠️ Order already has {existing_sources.count()} payment source(s):")
            for source in existing_sources:
                print(f"  - {source.source_type.name}: £{source.amount_allocated}")
            return
        
        print("🔍 No payment sources found. Creating Worldpay Gateway source...")
        
        # Get or create Worldpay Gateway source type
        source_type, created = SourceType.objects.get_or_create(
            name='Worldpay Gateway',
            defaults={'code': 'worldpay-gateway'}
        )
        
        if created:
            print(f"✅ Created new source type: {source_type.name}")
        else:
            print(f"✅ Using existing source type: {source_type.name}")
        
        # Create payment source
        payment_source = Source.objects.create(
            source_type=source_type,
            order=order,
            currency=order.currency,
            amount_allocated=order.total_incl_tax,
            amount_debited=order.total_incl_tax,
            reference=f"WP-{order.number}",  # Generic reference since we don't have the actual payment ID
            label="Worldpay Gateway Payment"
        )
        
        print(f"✅ Created payment source: {payment_source.reference}")
        print(f"   Amount allocated: £{payment_source.amount_allocated}")
        print(f"   Amount debited: £{payment_source.amount_debited}")
        
        # Create transaction record
        transaction = Transaction.objects.create(
            source=payment_source,
            txn_type='Debit',
            amount=order.total_incl_tax,
            reference=f"WP-AUTH-{order.number}",
            status='Complete'
        )
        
        print(f"✅ Created transaction: {transaction.reference}")
        print(f"   Type: {transaction.txn_type}")
        print(f"   Amount: £{transaction.amount}")
        print(f"   Status: {transaction.status}")
        
        # Update order status if needed
        if not order.status:
            order.status = 'Being processed'
            order.save()
            print(f"✅ Updated order status to: {order.status}")
        
        print("\n🎉 Payment source fix completed successfully!")
        print(f"Order {order.number} now has proper payment source linkage.")
        
    except Order.DoesNotExist:
        print(f"❌ Order {order_number} not found")
    except Exception as e:
        print(f"❌ Error fixing payment source: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_missing_payment_source("100004-8138")

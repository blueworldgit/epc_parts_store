#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from oscar.apps.order.models import Order
from oscar.apps.payment.models import Source, Transaction

print("🔍 CHECKING LATEST ORDER AFTER RECENT TEST")
print("=" * 50)

# Get the most recent order
try:
    latest_order = Order.objects.latest('date_placed')
    print(f"📋 Latest Order: {latest_order.number}")
    print(f"   📅 Date: {latest_order.date_placed}")
    print(f"   👤 Email: {latest_order.user.email if latest_order.user else latest_order.guest_email}")
    print(f"   💰 Total: £{latest_order.total_incl_tax}")
    print(f"   📊 Status: '{latest_order.status}'")
    
    # Check payment sources
    sources = latest_order.sources.all()
    print(f"\n💳 Payment Sources: {sources.count()}")
    
    if sources.count() > 0:
        for source in sources:
            print(f"   ✅ {source.source_type.name}: £{source.amount_allocated}")
            print(f"      Reference: {source.reference}")
            print(f"      Order Link: {source.order_id}")
            
            # Check transactions
            transactions = source.transactions.all()
            print(f"   💸 Transactions: {transactions.count()}")
            for txn in transactions:
                print(f"      {txn.txn_type}: £{txn.amount} - {txn.status}")
                print(f"       Reference: {txn.reference}")
    else:
        print("   ❌ NO PAYMENT SOURCES")
        
    print(f"\n🎯 DIAGNOSIS:")
    if sources.count() > 0:
        print("   ✅ Payment source creation IS working now!")
        print("   🔍 Issue must be in the thank-you page redirect logic")
        print("   🔍 Check Oscar's ThankYouView for session validation")
    else:
        print("   ❌ Payment source creation still failing")
        print("   🔍 Need to debug facade _create_payment_records method")
        
except Order.DoesNotExist:
    print("❌ No orders found")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

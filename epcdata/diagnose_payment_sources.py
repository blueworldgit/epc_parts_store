#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from oscar.apps.order.models import Order
from oscar.apps.payment.models import Source, SourceType, Transaction

print("🔍 DETAILED ANALYSIS: Why Payment Sources Aren't Being Created")
print("=" * 70)

# Check recent orders 
recent_orders = Order.objects.all().order_by('-date_placed')[:5]

print("📋 RECENT ORDERS ANALYSIS:")
for order in recent_orders:
    print(f"\n   Order: {order.number}")
    print(f"   Date: {order.date_placed}")
    print(f"   Email: {order.user.email if order.user else order.guest_email}")
    print(f"   Status: '{order.status}'")
    print(f"   Total: £{order.total_incl_tax}")
    
    # Check payment sources
    sources = order.sources.all()
    print(f"   Payment Sources: {sources.count()}")
    
    if sources.count() == 0:
        print(f"   ❌ NO PAYMENT SOURCE - This confirms the issue!")

print(f"\n🔍 CHECKING PAYMENT SOURCE TYPES:")
source_types = SourceType.objects.all()
print(f"Available source types: {source_types.count()}")
for st in source_types:
    print(f"   - {st.name} (code: {st.code})")

print(f"\n🔍 CHECKING ALL PAYMENT SOURCES:")
all_sources = Source.objects.all()
print(f"Total payment sources in system: {all_sources.count()}")

print(f"\n🔍 CHECKING ALL TRANSACTIONS:")
all_transactions = Transaction.objects.all()
print(f"Total transactions in system: {all_transactions.count()}")

print(f"\n💡 CONCLUSION:")
if all_sources.count() == 0:
    print(f"   ❌ NO payment sources exist - the _create_payment_source method is not being called")
    print(f"   🔍 This means either:")
    print(f"       1. The payment is failing before reaching _create_payment_source")
    print(f"       2. There's an exception in _create_payment_source that's being caught")
    print(f"       3. The success condition is not being met")
else:
    print(f"   ✅ Some payment sources exist - check why recent ones don't have them")

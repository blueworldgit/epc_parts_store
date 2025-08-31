#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from oscar.apps.order.models import Order
from oscar.apps.payment.models import SourceType, Source, Transaction

print("=== COMPARING CARD ORDERS ===")
print()

# Get recent orders
recent_orders = Order.objects.all().order_by('-date_placed')[:10]

print("📋 Recent Orders:")
for order in recent_orders:
    print(f"   {order.number} - {order.date_placed} - £{order.total_incl_tax} - {order.status}")
    
    # Check payment sources
    payment_sources = Source.objects.filter(order=order)
    if payment_sources.exists():
        print(f"     ✅ Has {payment_sources.count()} payment source(s)")
        for source in payment_sources:
            print(f"        💳 {source.source_type.name}: £{source.amount_allocated}")
            transactions = Transaction.objects.filter(source=source)
            for txn in transactions:
                print(f"          📝 {txn.txn_type}: £{txn.amount} - {txn.status}")
    else:
        print(f"     ❌ No payment sources")
    print()

print("\n=== SPECIFIC CARD ANALYSIS ===")

# Look for patterns in working vs non-working orders
orders_with_sources = []
orders_without_sources = []

for order in recent_orders:
    payment_sources = Source.objects.filter(order=order)
    if payment_sources.exists():
        orders_with_sources.append(order)
    else:
        orders_without_sources.append(order)

print(f"📊 Orders WITH payment sources: {len(orders_with_sources)}")
for order in orders_with_sources:
    print(f"   ✅ {order.number} - {order.date_placed}")

print(f"\n📊 Orders WITHOUT payment sources: {len(orders_without_sources)}")
for order in orders_without_sources:
    print(f"   ❌ {order.number} - {order.date_placed}")

# Check if there's a pattern based on timing
print(f"\n=== TIMING ANALYSIS ===")
if orders_with_sources and orders_without_sources:
    latest_working = max(orders_with_sources, key=lambda x: x.date_placed)
    latest_broken = max(orders_without_sources, key=lambda x: x.date_placed)
    
    print(f"Latest working order: {latest_working.number} at {latest_working.date_placed}")
    print(f"Latest broken order: {latest_broken.number} at {latest_broken.date_placed}")
    
    if latest_broken.date_placed > latest_working.date_placed:
        print("🔍 Pattern: Broken orders are MORE RECENT - suggests recent code change broke payment linking")
    else:
        print("🔍 Pattern: Mixed timing - suggests intermittent issue")

#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from oscar.apps.order.models import Order

order_number = '100004-926'

print(f"🔍 INVESTIGATING ORDER {order_number} - Billing address test")
print("=" * 60)

try:
    order = Order.objects.get(number=order_number)
    print(f'✅ Found Order: {order.number}')
    print(f'   📅 Date: {order.date_placed}')
    print(f'   💰 Total: £{order.total_incl_tax}')
    print(f'   📊 Status: "{order.status}"')
    print(f'   👤 Email: {order.user.email if order.user else order.guest_email}')
    
    # Check payment sources
    payment_sources = order.sources.all()
    print(f'\n💳 Payment Sources ({payment_sources.count()}):')
    
    if payment_sources:
        for source in payment_sources:
            print(f'   ✅ {source.source_type.name}: £{source.amount_allocated}')
            print(f'      Reference: {source.reference}')
        print(f'   🎉 SUCCESS: Payment source was created!')
    else:
        print(f'   ❌ NO PAYMENT SOURCES - Payment processing still failing')
        
    print(f'\n🏠 Address used:')
    if order.billing_address:
        print(f'   Postcode: {order.billing_address.postcode}')
        print(f'   Line1: {order.billing_address.line1}')
        print(f'   City: {order.billing_address.line4}')
    
    print(f'\n🔍 CONCLUSION:')
    if payment_sources.count() > 0:
        print(f'   ✅ Billing address removal worked - payment source created!')
        print(f'   ✅ But still redirected instead of showing thank-you page')
        print(f'   🔍 This means there are TWO separate issues:')
        print(f'      1. Billing address prevents payment source creation')
        print(f'      2. Something else causes the redirect problem')
    else:
        print(f'   ❌ Billing address removal did not fix payment source creation')
        print(f'   🔍 The issue is deeper than just billing address')

except Order.DoesNotExist:
    print(f'❌ Order {order_number} not found')
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()

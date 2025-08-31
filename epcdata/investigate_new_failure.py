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

order_number = '100004-9856'

print(f"🚨 URGENT: Investigating JASON PINK card redirect issue")
print(f"📋 Order: {order_number}")
print("=" * 60)

try:
    order = Order.objects.get(number=order_number)
    print(f'✅ Found Order: {order.number}')
    print(f'   📅 Date: {order.date_placed}')
    print(f'   💰 Total: £{order.total_incl_tax}')
    print(f'   📊 Status: "{order.status}"')
    print(f'   👤 Email: {order.user.email if order.user else order.guest_email}')
    
    # Check if payment source was created (our new fix)
    payment_sources = order.sources.all()
    print(f'\n💳 Payment Sources ({payment_sources.count()}):')
    
    if payment_sources:
        for source in payment_sources:
            print(f'   ✅ {source.source_type.name}: £{source.amount_allocated}')
            print(f'      Reference: {source.reference}')
            print(f'      Label: {source.label}')
    else:
        print(f'   ❌ NO PAYMENT SOURCES - FIX NOT WORKING!')
        
    print(f'\n🔍 ANALYSIS:')
    print(f'   - Order exists: ✅')
    print(f'   - Payment processed at Worldpay: ✅ (you confirmed)')
    print(f'   - Redirected to catalogue instead of thank-you: ❌')
    print(f'   - Payment source created: {"✅" if payment_sources else "❌"}')
    
    if not payment_sources:
        print(f'\n🚨 CONCLUSION: Fix is not working!')
        print(f'   Either the code fix wasn\'t applied, or there\'s another issue')

except Order.DoesNotExist:
    print(f'❌ Order {order_number} not found')
    print(f'🚨 This means order creation failed completely!')
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()

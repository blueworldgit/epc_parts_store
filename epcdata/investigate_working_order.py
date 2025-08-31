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

order_number = '100001-9108'

try:
    order = Order.objects.get(number=order_number)
    print(f'✅ Found Order: {order.number}')
    print(f'   📅 Date: {order.date_placed}')
    print(f'   💰 Total: £{order.total_incl_tax}')
    print(f'   📊 Status: {order.status}')
    print(f'   👤 User: {order.user.email if order.user else order.guest_email}')
    print(f'   🏠 Shipping: {order.shipping_address}')
    
    # Check payment sources
    payment_sources = order.sources.all()
    print(f'\n💳 Payment Sources ({payment_sources.count()}):')
    
    if payment_sources:
        for source in payment_sources:
            print(f'   ✅ {source.source_type.name}: £{source.amount_allocated}')
            print(f'      Reference: {source.reference}')
            print(f'      Label: {source.label}')
            
            # Check transactions
            transactions = source.transactions.all()
            print(f'   💸 Transactions ({transactions.count()}):')
            for txn in transactions:
                print(f'       {txn.txn_type}: £{txn.amount} - {txn.status}')
                print(f'        Date: {txn.date_created}')
                print(f'        Reference: {txn.reference}')
    else:
        print('   ❌ No payment sources found')

    # Compare with the problematic order
    print(f'\n🔍 COMPARISON WITH PROBLEMATIC ORDER 100004-8138:')
    try:
        problem_order = Order.objects.get(number='100004-8138')
        problem_sources = problem_order.sources.all()
        print(f'   Working Order Sources: {payment_sources.count()}')
        print(f'   Problem Order Sources: {problem_sources.count()}')
        
        print(f'\n   Working Order Status: {order.status}')
        print(f'   Problem Order Status: {problem_order.status}')
        
    except Order.DoesNotExist:
        print('   Problem order not found for comparison')

except Order.DoesNotExist:
    print(f'❌ Order {order_number} not found')
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()

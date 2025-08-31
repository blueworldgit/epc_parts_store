#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from oscar.apps.order.models import Order
from oscar.apps.payment.models import Source

try:
    order = Order.objects.get(number='100004-1610')
    print(f'✅ Order: {order.number}')
    print(f'   Date: {order.date_placed}')
    print(f'   Total: £{order.total_incl_tax}')
    print(f'   Status: "{order.status}"')
    
    sources = order.sources.all()
    print(f'   Payment Sources: {sources.count()}')
    
    if sources.count() > 0:
        for source in sources:
            print(f'   ✅ Source: {source.source_type.name}')
            print(f'      Amount: £{source.amount_allocated}')
            print(f'      Reference: {source.reference}')
            print(f'      Transactions: {source.transactions.count()}')
        print('🎉 SUCCESS: Payment source exists!')
    else:
        print('❌ NO payment sources found')
        
except Order.DoesNotExist:
    print('❌ Order not found')
except Exception as e:
    print(f'❌ Error: {e}')

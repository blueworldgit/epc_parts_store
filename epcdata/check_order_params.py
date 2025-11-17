#!/usr/bin/env python
"""
Simple test to check OrderCreator parameters for shipping
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from decimal import Decimal
from oscar.core.loading import get_model
from oscar.apps.order.utils import OrderCreator
from oscar.core import prices
from oscar.apps.shipping.methods import FixedPrice
import inspect

def check_order_creator():
    """Check what parameters OrderCreator.place_order accepts"""
    
    print("🔍 Checking OrderCreator.place_order Parameters")
    print("=" * 50)
    
    try:
        order_creator = OrderCreator()
        place_order_method = order_creator.place_order
        
        # Get method signature
        sig = inspect.signature(place_order_method)
        print(f"📋 place_order signature:")
        print(f"   {place_order_method.__name__}{sig}")
        
        print(f"\\n📋 Parameters:")
        for param_name, param in sig.parameters.items():
            default = param.default if param.default != inspect.Parameter.empty else "Required"
            print(f"   • {param_name}: {default}")
        
        # Check Order model fields
        Order = get_model('order', 'Order')
        field_names = [f.name for f in Order._meta.get_fields()]
        shipping_fields = [f for f in field_names if 'shipping' in f.lower()]
        
        print(f"\\n📦 Order model shipping fields:")
        for field in shipping_fields:
            print(f"   • {field}")
        
        print(f"\\n📋 All Order model fields:")
        print(f"   {', '.join(sorted(field_names))}")
        
        # Check if we have shipping fields
        has_shipping_incl_tax = 'shipping_incl_tax' in field_names
        has_shipping_method = 'shipping_method' in field_names
        
        print(f"\\n✅ Analysis:")
        print(f"   • Has shipping_incl_tax field: {has_shipping_incl_tax}")
        print(f"   • Has shipping_method field: {has_shipping_method}")
        
        if not has_shipping_incl_tax:
            print(f"   ⚠️ Order model missing shipping_incl_tax field!")
        if not has_shipping_method:
            print(f"   ⚠️ Order model missing shipping_method field!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_order_creator()
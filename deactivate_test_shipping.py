#!/usr/bin/env python
"""
Script to deactivate test shipping method (20p shipping)
Run this on the production server
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from motorpartsdata.models import ShippingMethod

# Find and deactivate test shipping
test_shipping = ShippingMethod.objects.filter(price=0.20).first()

if test_shipping:
    print(f"Found test shipping: {test_shipping.name} - £{test_shipping.price}")
    print(f"Current status: {'Active' if test_shipping.is_active else 'Inactive'}")
    
    if test_shipping.is_active:
        test_shipping.is_active = False
        test_shipping.save()
        print("✅ Test shipping has been DEACTIVATED")
    else:
        print("ℹ️ Test shipping is already inactive")
else:
    # Try finding by name
    test_shipping = ShippingMethod.objects.filter(name__icontains='test').first()
    if test_shipping:
        print(f"Found: {test_shipping.name} - £{test_shipping.price}")
        print(f"Current status: {'Active' if test_shipping.is_active else 'Inactive'}")
        
        if test_shipping.is_active:
            test_shipping.is_active = False
            test_shipping.save()
            print("✅ Test shipping has been DEACTIVATED")
        else:
            print("ℹ️ Test shipping is already inactive")
    else:
        print("❌ No test shipping method found")
        print("\nAll shipping methods:")
        for s in ShippingMethod.objects.all():
            status = '✅ Active' if s.is_active else '❌ Inactive'
            print(f"  {status} | ID: {s.id} | {s.name} - £{s.price}")

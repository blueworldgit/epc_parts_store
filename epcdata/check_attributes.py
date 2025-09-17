#!/usr/bin/env python
import os
import sys
import django

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')

# Setup Django
django.setup()

from oscar.apps.catalogue.models import Product, ProductAttributeValue

print("Checking call_out_order attributes...")

# Check total count
total_count = ProductAttributeValue.objects.filter(attribute__code='call_out_order').count()
print(f"Total products with call_out_order: {total_count}")

if total_count > 0:
    print("\nSample products with call_out_order:")
    values = ProductAttributeValue.objects.filter(attribute__code='call_out_order')[:5]
    for val in values:
        print(f"  Product: {val.product.upc} | Call-out: {val.value_text} | Title: {val.product.title[:40]}...")

# Check other attributes too
for attr_code in ['orientation', 'part_remark', 'part_note']:
    count = ProductAttributeValue.objects.filter(attribute__code=attr_code).count()
    print(f"Products with {attr_code}: {count}")
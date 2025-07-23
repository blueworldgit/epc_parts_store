#!/usr/bin/env python
"""
Debug script to check import data status
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from motorpartsdata.models import Part, PricingData
from oscar.apps.catalogue.models import Product
from oscar.apps.partner.models import StockRecord

print("=== Data Status ===")
print(f"Parts: {Part.objects.count()}")
print(f"PricingData: {PricingData.objects.count()}")
print(f"Oscar Products: {Product.objects.count()}")
print(f"StockRecords: {StockRecord.objects.count()}")
print()

# Check sample data
sample_part = Part.objects.first()
if sample_part:
    print(f"Sample part: {sample_part.part_number} - {sample_part.usage_name}")
    
    # Check if pricing exists
    pricing = PricingData.objects.filter(part_number=sample_part).first()
    print(f"Has pricing: {pricing is not None}")
    if pricing:
        print(f"List price: {pricing.list_price}")
        print(f"Stock available: {pricing.stock_available}")
    
    # Check Oscar product
    oscar_product = Product.objects.filter(upc=f"EPC-{sample_part.part_number}").first()
    print(f"Has Oscar product: {oscar_product is not None}")
    if oscar_product:
        print(f"Oscar product: {oscar_product.title}")
        
        # Check stock record
        stock_record = StockRecord.objects.filter(product=oscar_product).first()
        print(f"Has stock record: {stock_record is not None}")
        if stock_record:
            print(f"Stock record price: {stock_record.price}")
            print(f"Stock record inventory: {stock_record.num_in_stock}")

print()
print("=== Parts with pricing (first 5) ===")
parts_with_pricing = Part.objects.filter(pricing_data__isnull=False)[:5]
for part in parts_with_pricing:
    pricing = part.pricing_data.first()
    print(f"- {part.part_number}: £{pricing.list_price if pricing and pricing.list_price else 'N/A'}")

print()
print("=== Products without stock records (first 5) ===")
products_without_stock = Product.objects.filter(stockrecords__isnull=True)[:5]
for product in products_without_stock:
    print(f"- {product.upc}: {product.title}")

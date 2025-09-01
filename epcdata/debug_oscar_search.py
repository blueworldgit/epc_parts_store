#!/usr/bin/env python3
"""
Quick Oscar Database Check
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, '/path/to/your/django/project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from catalogue.models import Product
from partner.models import StockRecord

def check_part_in_oscar(part_number):
    print(f"🔍 Searching for {part_number} in Oscar database...")
    
    # Search by UPC
    products_by_upc = Product.objects.filter(upc=part_number)
    print(f"  📦 Products with UPC '{part_number}': {products_by_upc.count()}")
    
    # Search by title containing part number
    products_by_title = Product.objects.filter(title__icontains=part_number)
    print(f"  📦 Products with title containing '{part_number}': {products_by_title.count()}")
    
    # Show some results
    for product in products_by_upc:
        stock_records = StockRecord.objects.filter(product=product)
        stock_count = stock_records.first().num_in_stock if stock_records.exists() else 0
        price = stock_records.first().price if stock_records.exists() else "No price"
        print(f"    ✅ Found: {product.title} | Stock: {stock_count} | Price: {price}")
    
    for product in products_by_title:
        if product not in products_by_upc:  # Don't duplicate
            stock_records = StockRecord.objects.filter(product=product)
            stock_count = stock_records.first().num_in_stock if stock_records.exists() else 0
            price = stock_records.first().price if stock_records.exists() else "No price"
            print(f"    ✅ Found in title: {product.title} | Stock: {stock_count} | Price: {price}")
    
    # Show total Oscar products
    total_products = Product.objects.count()
    print(f"  📊 Total Oscar products in database: {total_products}")
    
    # Show sample products
    sample_products = Product.objects.filter(upc__isnull=False)[:3]
    print(f"  📋 Sample Oscar products:")
    for product in sample_products:
        print(f"    • UPC: {product.upc} | Title: {product.title[:50]}...")

if __name__ == "__main__":
    check_part_in_oscar("C00112285")

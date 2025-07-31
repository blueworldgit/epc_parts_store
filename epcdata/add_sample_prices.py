#!/usr/bin/env python3
"""
Simple script to add sample prices to Oscar StockRecord objects
"""
import os
import sys
import django
from decimal import Decimal
import random

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from oscar.apps.partner.models import StockRecord

def add_sample_prices():
    """Add sample prices to stock records that don't have prices"""
    stock_records = StockRecord.objects.filter(price__isnull=True)
    print(f"Found {stock_records.count()} stock records without prices")
    
    updated_count = 0
    
    for stock_record in stock_records:
        # Generate a random price between 10.00 and 500.00
        sample_price = Decimal(str(round(random.uniform(10.00, 500.00), 2)))
        
        stock_record.price = sample_price
        stock_record.save()
        
        updated_count += 1
        if updated_count % 100 == 0:
            print(f"Updated {updated_count} records...")
    
    print(f"Successfully added sample prices to {updated_count} stock records")
    print("All prices are in GBP currency")

if __name__ == "__main__":
    print("Adding sample prices to stock records...")
    add_sample_prices()
    print("Done!")

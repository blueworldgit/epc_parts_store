#!/usr/bin/env python
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from oscar.apps.catalogue.models import Category, Product

def find_serial_categories():
    print("🔍 FINDING ALL SERIAL CATEGORIES")
    print("=" * 60)
    
    # Look for categories containing "LSFAL11A4PA157987"
    lsfal_categories = Category.objects.filter(name__contains="LSFAL11A4PA157987")
    
    if lsfal_categories:
        print("Found these categories containing LSFAL11A4PA157987:")
        for cat in lsfal_categories:
            print(f"  📁 {cat.name} (depth={cat.depth})")
            print(f"     Slug: {cat.slug}")
            print(f"     URL: {cat.get_absolute_url()}")
            print(f"     Products: {cat.product_set.count()}")
            print()
    else:
        print("❌ No categories found containing LSFAL11A4PA157987")
    
    # Also look for the specific parent category we know exists
    charging_cat = Category.objects.filter(name="Charging & Energystorage")
    
    if charging_cat:
        print("\nFound 'Charging & Energystorage' categories:")
        for cat in charging_cat:
            print(f"  📁 {cat.name} (depth={cat.depth})")
            print(f"     Slug: {cat.slug}")
            print(f"     URL: {cat.get_absolute_url()}")
            print(f"     Products: {cat.product_set.count()}")
            
            # Check parent hierarchy
            current = cat
            path = []
            while current:
                path.insert(0, current.name)
                current = current.get_parent()
            print(f"     Path: {' > '.join(path)}")
            print()

if __name__ == "__main__":
    find_serial_categories()
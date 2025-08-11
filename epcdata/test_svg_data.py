#!/usr/bin/env python
"""
Quick test script to check SVG data and products
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from motorpartsdata.models import Part, ChildTitle
from catalogue.models import Product

def test_svg_data():
    print("=== Testing SVG Data ===")
    
    # Check ChildTitle objects with SVG
    child_titles_with_svg = ChildTitle.objects.filter(svg_code__isnull=False).exclude(svg_code='')[:5]
    print(f"\nChildTitles with SVG: {child_titles_with_svg.count()}")
    
    for ct in child_titles_with_svg:
        print(f"ChildTitle: {ct.title} - SVG length: {len(ct.svg_code) if ct.svg_code else 0}")
        
        # Find parts linked to this ChildTitle
        parts = Part.objects.filter(child_title=ct)[:3]
        print(f"  Linked parts: {parts.count()}")
        
        for part in parts:
            print(f"    Part: {part.part_number}")
            
            # Check if there's a Product with this UPC
            try:
                product = Product.objects.get(upc=part.part_number)
                print(f"      Product found: {product.title} (ID: {product.id})")
                print(f"      URL: http://127.0.0.1:8000/catalogue/{product.id}/")
            except Product.DoesNotExist:
                print(f"      No product found with UPC: {part.part_number}")
        print()

if __name__ == "__main__":
    test_svg_data()

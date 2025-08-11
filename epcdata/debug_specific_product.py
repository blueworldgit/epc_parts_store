#!/usr/bin/env python
"""
Debug specific product SVG data
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from oscar.apps.catalogue.models import Product
from motorpartsdata.models import Part, ChildTitle

def debug_product(product_slug):
    print(f"=== Debugging Product: {product_slug} ===")
    
    try:
        # Find the product
        product = Product.objects.get(slug=product_slug)
        print(f"✅ Product found: {product.title}")
        print(f"   ID: {product.id}")
        print(f"   UPC: {product.upc}")
        print(f"   Slug: {product.slug}")
        
        # Check for primary image
        if product.primary_image:
            print(f"   Primary Image: {product.primary_image}")
            if product.primary_image.original:
                print(f"   Image URL: {product.primary_image.original.url}")
        else:
            print("   ❌ No primary image")
        
        # Check for SVG data using the UPC
        if product.upc:
            print(f"\n🔍 Checking SVG data for UPC: {product.upc}")
            try:
                part = Part.objects.get(part_number=product.upc)
                print(f"   ✅ Part found: {part.part_number}")
                
                if part.child_title:
                    print(f"   ✅ ChildTitle found: {part.child_title.title}")
                    
                    if part.child_title.svg_code:
                        svg_length = len(part.child_title.svg_code)
                        print(f"   ✅ SVG data found: {svg_length} characters")
                        
                        # Show first 200 characters of SVG
                        svg_preview = part.child_title.svg_code[:200]
                        print(f"   SVG Preview: {svg_preview}...")
                    else:
                        print(f"   ❌ No SVG data in ChildTitle")
                else:
                    print(f"   ❌ No ChildTitle linked to part")
                    
            except Part.DoesNotExist:
                print(f"   ❌ No part found with UPC: {product.upc}")
        else:
            print("   ❌ Product has no UPC")
            
    except Product.DoesNotExist:
        print(f"❌ Product not found with slug: {product_slug}")

if __name__ == "__main__":
    debug_product("part-c00077193_2378")

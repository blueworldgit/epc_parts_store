#!/usr/bin/env python
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from oscar.apps.catalogue.models import Category, Product
from motorpartsdata.models import Part, ChildTitle, ParentTitle

def check_all_lsfal_categories():
    """Check all categories under LSFAL11A4PA157987 serial"""
    print("🔍 ALL CATEGORIES UNDER LSFAL11A4PA157987 SERIAL")
    print("=" * 60)
    
    # Find the serial category
    serial_cat = Category.objects.filter(name="Serial LSFAL11A4PA157987").first()
    if not serial_cat:
        print("❌ Serial category not found")
        return
    
    print(f"📁 Serial: {serial_cat.name}")
    print(f"   URL: {serial_cat.get_absolute_url()}")
    print()
    
    # Get all parent categories under this serial
    parent_categories = Category.objects.filter(path__startswith=serial_cat.path, depth=serial_cat.depth + 1)
    
    for parent_cat in parent_categories:
        print(f"📁 Parent: {parent_cat.name}")
        print(f"   Products: {parent_cat.product_set.count()}")
        print(f"   URL: {parent_cat.get_absolute_url()}")
        
        # Show first few products in parent category if any
        parent_products = parent_cat.product_set.all()[:3]
        if parent_products:
            print(f"   📦 Sample products in parent:")
            for product in parent_products:
                print(f"      - {product.upc}: {product.title}")
        
        # Get child categories
        child_categories = Category.objects.filter(path__startswith=parent_cat.path, depth=parent_cat.depth + 1)
        
        for child_cat in child_categories:
            print(f"  📂 Child: {child_cat.name}")
            print(f"     Products: {child_cat.product_set.count()}")
            print(f"     URL: {child_cat.get_absolute_url()}")
            
            # Show first few products in this child category
            products = child_cat.product_set.all()[:3]
            if products:
                print(f"       📦 Sample products:")
                for product in products:
                    print(f"         - {product.upc}: {product.title}")
        
        print()
    
    print("\n" + "=" * 60)
    print("🔍 SUMMARY OF PRODUCT DISTRIBUTION")
    print("=" * 60)
    
    total_products = 0
    for parent_cat in parent_categories:
        parent_products = parent_cat.product_set.count()
        child_products = sum(child.product_set.count() for child in Category.objects.filter(path__startswith=parent_cat.path, depth=parent_cat.depth + 1))
        
        print(f"📁 {parent_cat.name}: {parent_products} in parent, {child_products} in children")
        total_products += parent_products + child_products
    
    print(f"\n📊 Total products in LSFAL11A4PA157987: {total_products}")
    
    # Let's also check what the products in the parent category should be
    print("\n" + "=" * 60)
    print("🔍 DETAILED ANALYSIS OF MISPLACED PRODUCTS")
    print("=" * 60)
    
    charging_parent = Category.objects.filter(
        name="Charging & Energystorage",
        slug="serial-LSFAL11A4PA157987-parent-12"
    ).first()
    
    if charging_parent and charging_parent.product_set.count() > 0:
        print(f"📁 {charging_parent.name} has {charging_parent.product_set.count()} products")
        print("   These products should be in their correct categories:")
        
        from motorpartsdata.models import Part
        
        for product in charging_parent.product_set.all():
            try:
                part = Part.objects.filter(part_number=product.upc).first()
                if part:
                    print(f"   - {product.upc}: Should be in '{part.child_title.parent.title}' -> '{part.child_title.title}'")
                else:
                    print(f"   - {product.upc}: Not found in EPC data")
            except Exception as e:
                print(f"   - {product.upc}: Error - {e}")

if __name__ == "__main__":
    check_all_lsfal_categories()
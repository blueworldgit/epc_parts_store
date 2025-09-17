#!/usr/bin/env python
import os
import sys
import django

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from oscar.apps.catalogue.models import Category, Product
from motorpartsdata.models import Part

def debug_category_products():
    print("============================================================")
    print("🔍 CATEGORY PRODUCTS DIAGNOSTIC")
    print("============================================================")
    
    # Find the specific category
    category_name = "serial-LSFAL11A4PA157987-parent-12-child-1_40"
    try:
        category = Category.objects.get(name=category_name)
        print(f"✅ Category found: {category.name}")
        print(f"   Full path: {category.get_absolute_url()}")
        print(f"   Category ID: {category.id}")
        print(f"   Depth: {category.depth}")
        print(f"   Parent: {category.get_parent()}")
        print()
        
        # Check products directly assigned to this category
        direct_products = category.product_set.all()
        print(f"📦 Products directly in this category: {direct_products.count()}")
        
        if direct_products.exists():
            for product in direct_products[:5]:  # Show first 5
                print(f"   - {product.title} (UPC: {product.upc})")
        print()
        
        # Check products in child categories
        child_categories = category.get_children()
        print(f"👶 Child categories: {child_categories.count()}")
        
        total_products_in_children = 0
        for child in child_categories:
            child_products = child.product_set.all()
            total_products_in_children += child_products.count()
            if child_products.exists():
                print(f"   - {child.name}: {child_products.count()} products")
        
        print(f"📊 Total products in child categories: {total_products_in_children}")
        print()
        
        # Check if any Parts should belong to this category
        print("🔍 CHECKING SOURCE DATA:")
        parts_query = Part.objects.filter(
            serial_number__serial_number__contains="LSFAL11A4PA157987",
            parent_number="12",
            child_number="1.40"
        )
        print(f"📋 Parts matching category criteria: {parts_query.count()}")
        
        if parts_query.exists():
            print("   Sample parts that should be in this category:")
            for part in parts_query[:3]:
                print(f"   - {part.part_number}: {part.description}")
                # Check if this part has been imported to Oscar
                try:
                    oscar_product = Product.objects.get(upc=part.part_number)
                    print(f"     ✅ Found in Oscar: {oscar_product.title}")
                    categories = oscar_product.categories.all()
                    print(f"     📂 Current categories: {[cat.name for cat in categories]}")
                except Product.DoesNotExist:
                    print(f"     ❌ NOT found in Oscar products")
        else:
            print("   ❌ No matching parts found in source data")
        
    except Category.DoesNotExist:
        print(f"❌ Category not found: {category_name}")
        print("\n🔍 Similar categories:")
        similar = Category.objects.filter(name__contains="LSFAL11A4PA157987")
        for cat in similar[:10]:
            print(f"   - {cat.name} (products: {cat.product_set.count()})")

if __name__ == "__main__":
    debug_category_products()
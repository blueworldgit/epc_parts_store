#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from catalogue.models import Category, Product

def check_category_fix():
    print("🔍 Checking category fix results...")
    
    # Check the specific child category from the URL
    child_slug = 'serial-LSFAL11A4PA157987-parent-12-child-1_40'
    child_category = Category.objects.filter(slug=child_slug).first()
    
    if child_category:
        print(f"✅ Child category found: {child_category.name}")
        products = Product.objects.filter(categories=child_category)
        print(f"Products in child category: {products.count()}")
        
        if products.exists():
            print("Sample products in child category:")
            for product in products[:3]:
                print(f"  - {product.title}")
        else:
            print("❌ No products in child category")
    else:
        print(f"❌ Child category '{child_slug}' not found")
    
    # Check the parent category
    parent_slug = 'serial-LSFAL11A4PA157987-parent-12'
    parent_category = Category.objects.filter(slug=parent_slug).first()
    
    if parent_category:
        print(f"\n📁 Parent category found: {parent_category.name}")
        
        # Check products directly in parent
        products_in_parent = Product.objects.filter(categories=parent_category)
        print(f"Products directly in parent: {products_in_parent.count()}")
        
        # Check all child categories
        child_categories = parent_category.get_children()
        print(f"Child categories: {child_categories.count()}")
        
        total_products_in_children = 0
        for child in child_categories[:5]:  # Show first 5 children
            products_in_child = Product.objects.filter(categories=child)
            total_products_in_children += products_in_child.count()
            print(f"  - {child.slug}: {products_in_child.count()} products")
        
        if child_categories.count() > 5:
            print(f"  ... and {child_categories.count() - 5} more child categories")
            
        print(f"\nTotal products in child categories: {total_products_in_children}")
        
        # Check if there are still products in parent that should be in children
        if products_in_parent.count() > 0:
            print(f"⚠️  WARNING: {products_in_parent.count()} products still in parent category!")
            print("Sample products in parent:")
            for product in products_in_parent[:3]:
                print(f"  - {product.title}")
    else:
        print(f"❌ Parent category '{parent_slug}' not found")
    
    # Check overall LSFAL11A4PA157987 serial distribution
    print(f"\n📊 Overall LSFAL11A4PA157987 serial distribution:")
    serial_category = Category.objects.filter(slug='serial-lsfal11a4pa157987').first()
    if serial_category:
        all_descendants = serial_category.get_descendants()
        total_products = 0
        for cat in all_descendants:
            products = Product.objects.filter(categories=cat)
            if products.count() > 0:
                total_products += products.count()
                if cat.slug.endswith('-parent-12') or cat.slug.endswith('-parent-12-child-1_40'):
                    print(f"  {cat.slug}: {products.count()} products")
        
        print(f"Total products in serial: {total_products}")

if __name__ == '__main__':
    check_category_fix()
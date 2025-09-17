#!/usr/bin/env python
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from oscar.apps.catalogue.models import Category, Product

def check_actual_urls():
    print("============================================================")
    print("🔍 CHECKING ACTUAL CATEGORY URLS IN OSCAR")
    print("============================================================")
    
    # Find all categories related to LSFAL11A4PA157987
    lsfal_categories = Category.objects.filter(name__contains="LSFAL11A4PA157987").order_by('depth', 'path')
    
    print(f"📂 Categories containing 'LSFAL11A4PA157987': {lsfal_categories.count()}")
    
    for cat in lsfal_categories:
        product_count = cat.product_set.count()
        print(f"\n📁 {cat.name}")
        print(f"   Depth: {cat.depth}")
        print(f"   Slug: {cat.slug}")
        print(f"   Products: {product_count}")
        print(f"   Full URL: {cat.get_absolute_url()}")
        
        # Show children
        children = cat.get_children()
        if children.exists():
            print(f"   Children: {children.count()}")
            for child in children[:3]:  # Show first 3 children
                child_products = child.product_set.count()
                print(f"     └─ {child.name} ({child_products} products)")
                print(f"        URL: {child.get_absolute_url()}")
    
    print("\n" + "="*60)
    print("🔍 CHECKING CHARGING & ENERGYSTORAGE CATEGORIES")
    print("="*60)
    
    # Look for charging/energy categories specifically
    charging_cats = Category.objects.filter(name__icontains="charging")
    energy_cats = Category.objects.filter(name__icontains="energy")
    battery_cats = Category.objects.filter(name__icontains="battery")
    
    all_relevant = (charging_cats | energy_cats | battery_cats).distinct().order_by('depth', 'name')
    
    for cat in all_relevant:
        product_count = cat.product_set.count()
        print(f"\n🔋 {cat.name}")
        print(f"   Depth: {cat.depth}, Products: {product_count}")
        print(f"   URL: {cat.get_absolute_url()}")
        
        if product_count > 0:
            print("   Sample products:")
            for prod in cat.product_set.all()[:3]:
                print(f"     - {prod.upc}: {prod.title}")
    
    print("\n" + "="*60)
    print("🔍 CHECKING PARENT-12 PATTERN CATEGORIES")
    print("="*60)
    
    # Look for any categories with "parent-12" in slug or name
    parent_12_cats = Category.objects.filter(slug__contains="parent-12")
    
    for cat in parent_12_cats:
        product_count = cat.product_set.count()
        print(f"\n📁 {cat.name}")
        print(f"   Slug: {cat.slug}")
        print(f"   Products: {product_count}")
        print(f"   URL: {cat.get_absolute_url()}")
        
        # Check children
        children = cat.get_children()
        for child in children:
            child_products = child.product_set.count()
            print(f"     └─ {child.name} ({child_products} products)")
            print(f"        Slug: {child.slug}")
            print(f"        URL: {child.get_absolute_url()}")

if __name__ == "__main__":
    check_actual_urls()
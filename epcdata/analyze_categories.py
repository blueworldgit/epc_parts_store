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
from motorpartsdata.models import Part, SerialNumber

def analyze_working_vs_broken():
    print("============================================================")
    print("🔍 WORKING vs BROKEN CATEGORIES ANALYSIS")
    print("============================================================")
    
    # Find categories with products vs without
    all_categories = Category.objects.all()
    
    categories_with_products = []
    categories_without_products = []
    
    for category in all_categories:
        product_count = category.product_set.count()
        if product_count > 0:
            categories_with_products.append((category, product_count))
        else:
            categories_without_products.append(category)
    
    print(f"✅ Categories WITH products: {len(categories_with_products)}")
    print(f"❌ Categories WITHOUT products: {len(categories_without_products)}")
    print()
    
    # Show sample working categories
    print("🟢 WORKING CATEGORIES (with products):")
    for category, count in categories_with_products[:10]:
        print(f"   - {category.name} ({count} products, depth: {category.depth})")
        print(f"     URL: {category.get_absolute_url()}")
        if category.get_parent():
            print(f"     Parent: {category.get_parent().name}")
        print()
    
    # Show sample broken categories  
    print("🔴 EMPTY CATEGORIES (no products):")
    for category in categories_without_products[:10]:
        print(f"   - {category.name} (depth: {category.depth})")
        print(f"     URL: {category.get_absolute_url()}")
        if category.get_parent():
            print(f"     Parent: {category.get_parent().name}")
        print()
    
    # Check LSFAL11A4PA157987 specifically
    print("🔍 LSFAL11A4PA157987 SPECIFIC ANALYSIS:")
    lsfal_categories = Category.objects.filter(name__contains="LSFAL11A4PA157987")
    for cat in lsfal_categories:
        print(f"   - {cat.name}: {cat.product_set.count()} products")
        print(f"     Full path: {cat.get_absolute_url()}")
        
        # Check if there are children
        children = cat.get_children()
        if children.exists():
            print(f"     Children: {children.count()}")
            for child in children[:5]:
                print(f"       └─ {child.name}: {child.product_set.count()} products")
    
    # Pattern analysis
    print("\n📊 PATTERN ANALYSIS:")
    depth_stats = {}
    for category, count in categories_with_products:
        depth = category.depth
        if depth not in depth_stats:
            depth_stats[depth] = []
        depth_stats[depth].append((category.name, count))
    
    for depth in sorted(depth_stats.keys()):
        print(f"   Depth {depth}: {len(depth_stats[depth])} categories with products")
        # Show sample category names for each depth
        sample_names = [name for name, count in depth_stats[depth][:3]]
        print(f"     Examples: {', '.join(sample_names)}")

if __name__ == "__main__":
    analyze_working_vs_broken()
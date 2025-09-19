#!/usr/bin/env python
"""
Find Products for Serial

This script finds where products actually ended up for a specific serial,
even if some categories are empty.
"""

import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from oscar.apps.catalogue.models import Category, Product


def find_products_for_serial(serial):
    """Find all products and their distribution for a specific serial"""
    print(f"🔍 FINDING PRODUCTS FOR SERIAL: {serial}")
    print("="*60)
    
    # Get all categories for this serial
    all_categories = Category.objects.filter(slug__contains=f'serial-{serial}')
    child_categories = all_categories.filter(slug__contains='-child-').order_by('slug')
    
    print(f"Total categories for this serial: {all_categories.count()}")
    print(f"Child categories: {child_categories.count()}")
    
    # Check parent-2 specifically (the problematic one)
    parent_2_categories = child_categories.filter(slug__contains=f'serial-{serial}-parent-2-child-')
    
    print(f"\n🎯 PARENT-2 CATEGORIES (Energy Storage area):")
    print("-" * 50)
    
    total_products_parent_2 = 0
    for cat in parent_2_categories:
        product_count = cat.product_set.count()
        total_products_parent_2 += product_count
        status = "✅ HAS PRODUCTS" if product_count > 0 else "❌ EMPTY"
        print(f"{cat.slug}")
        print(f"  Name: '{cat.name}'")
        print(f"  Products: {product_count} {status}")
        
        # If it has products, show a few examples
        if product_count > 0:
            sample_products = cat.product_set.all()[:3]
            for product in sample_products:
                print(f"    • {product.title}")
            if product_count > 3:
                print(f"    ... and {product_count - 3} more")
        print()
    
    print(f"Total products in Parent-2: {total_products_parent_2}")
    
    # Check other parents that have products
    print(f"\n📊 OTHER PARENTS WITH PRODUCTS:")
    print("-" * 50)
    
    # Group by parent
    parent_stats = {}
    for cat in child_categories:
        # Extract parent number
        slug_parts = cat.slug.split('-parent-')
        if len(slug_parts) == 2:
            parent_part = slug_parts[1].split('-child-')[0]
            if parent_part not in parent_stats:
                parent_stats[parent_part] = {'categories': 0, 'products': 0, 'empty': 0}
            
            product_count = cat.product_set.count()
            parent_stats[parent_part]['categories'] += 1
            parent_stats[parent_part]['products'] += product_count
            if product_count == 0:
                parent_stats[parent_part]['empty'] += 1
    
    # Show top parents by product count
    sorted_parents = sorted(parent_stats.items(), key=lambda x: x[1]['products'], reverse=True)
    
    print("Top 10 parents by product count:")
    for parent_num, stats in sorted_parents[:10]:
        print(f"  Parent-{parent_num}: {stats['products']} products, {stats['categories']} categories, {stats['empty']} empty")
    
    # Check if there are any products for this serial at all
    total_products = sum(stats['products'] for stats in parent_stats.values())
    print(f"\n📈 SERIAL OVERVIEW:")
    print(f"  Total products across all categories: {total_products}")
    print(f"  Total categories: {child_categories.count()}")
    print(f"  Empty categories: {sum(stats['empty'] for stats in parent_stats.values())}")
    
    if total_products == 0:
        print("❌ NO PRODUCTS FOUND for this entire serial!")
        print("This might be:")
        print("  • A serial that exists in structure but has no imported products")
        print("  • A test/placeholder serial")
        print("  • A serial where import failed or was incomplete")
    
    # Check what serials DO have products
    print(f"\n🔍 CHECKING OTHER SERIALS WITH PRODUCTS:")
    print("-" * 50)
    
    # Find all serials that have products
    all_child_cats = Category.objects.filter(slug__contains='-child-')
    serial_product_counts = {}
    
    for cat in all_child_cats:
        if 'serial-' in cat.slug:
            parts = cat.slug.split('-')
            if len(parts) >= 3 and parts[0] == 'serial':
                serial_name = parts[1]
                if serial_name not in serial_product_counts:
                    serial_product_counts[serial_name] = 0
                serial_product_counts[serial_name] += cat.product_set.count()
    
    # Show serials with most products
    sorted_serials = sorted(serial_product_counts.items(), key=lambda x: x[1], reverse=True)
    
    print("Serials by product count:")
    for serial_name, product_count in sorted_serials:
        status = "✅ ACTIVE" if product_count > 0 else "❌ EMPTY"
        print(f"  {serial_name}: {product_count} products {status}")


if __name__ == "__main__":
    # Check the specific serial from the problematic URL
    serial = "LSFAL11A4PA157987"
    find_products_for_serial(serial)
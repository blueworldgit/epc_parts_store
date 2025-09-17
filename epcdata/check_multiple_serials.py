#!/usr/bin/env python
"""
Check Multiple Serials for Duplicate Issues

This script verifies that the consolidation worked across all serials
and checks if other serials had similar duplicate issues.
"""

import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from oscar.apps.catalogue.models import Category
from collections import defaultdict


def check_multiple_serials():
    """Check multiple serials for any remaining duplicate issues"""
    print("=== CHECKING MULTIPLE SERIALS FOR DUPLICATE ISSUES ===\n")

    # Find all unique serials
    all_categories = Category.objects.filter(slug__contains='-parent-').values_list('slug', flat=True)
    serials = set()
    
    for slug in all_categories:
        if 'serial-' in slug:
            parts = slug.split('-')
            if len(parts) >= 3 and parts[0] == 'serial':
                serial = parts[1]
                serials.add(serial)

    print(f"Found {len(list(all_categories))} total parent categories")
    print(f"Found {len(serials)} unique serials in database")
    print(f"Checking first 5 serials for any remaining issues...\n")

    # Check first 5 serials
    for i, serial in enumerate(list(serials)[:5], 1):
        print(f"{i}. Serial: {serial}")
        
        # Check for any remaining duplicate child categories
        child_categories = Category.objects.filter(slug__contains=f'serial-{serial}').filter(slug__contains='-child-')
        
        # Group by name to find duplicates
        name_groups = defaultdict(list)
        for cat in child_categories:
            name_groups[cat.name].append(cat)
        
        duplicates_found = 0
        categories_with_products = 0
        categories_empty = 0
        
        for name, cats in name_groups.items():
            if len(cats) > 1:
                duplicates_found += 1
                print(f"  ⚠ DUPLICATE STILL EXISTS: '{name}'")
                for cat in cats:
                    product_count = cat.product_set.count()
                    print(f"    {cat.slug} - Products: {product_count}")
            else:
                # Single category - check if it has products
                cat = cats[0]
                product_count = cat.product_set.count()
                if product_count > 0:
                    categories_with_products += 1
                else:
                    categories_empty += 1
        
        if duplicates_found == 0:
            print(f"  ✓ NO DUPLICATES FOUND - All categories are unique!")
        
        print(f"  Categories with products: {categories_with_products}")
        print(f"  Empty categories: {categories_empty}")
        
        # Check a sample parent to see if products are now in the right place
        sample_parent = Category.objects.filter(
            slug__contains=f'serial-{serial}-parent-'
        ).exclude(slug__contains='-child-').first()
        
        if sample_parent:
            parent_num = sample_parent.slug.split('-parent-')[1]
            child_1 = Category.objects.filter(
                slug=f'serial-{serial}-parent-{parent_num}-child-1'
            ).first()
            
            if child_1:
                product_count = child_1.product_set.count()
                print(f"  Sample check - Child-1 in parent-{parent_num}: {product_count} products")
                if product_count > 0:
                    print(f"    ✓ SUCCESS: Child-1 now has products!")
                else:
                    print(f"    ⚠ Note: Child-1 still empty (may be normal if no products belong there)")
        
        print()

    # Overall database health check
    print("=== OVERALL DATABASE HEALTH ===")
    
    # Count all child categories
    all_child_cats = Category.objects.filter(slug__contains='-child-')
    total_children = all_child_cats.count()
    
    # Check for any remaining duplicates across entire database
    name_groups = defaultdict(list)
    for cat in all_child_cats:
        # Group by name AND parent to detect true duplicates
        parent_part = cat.slug.split('-child-')[0] if '-child-' in cat.slug else 'unknown'
        key = f"{parent_part}::{cat.name}"
        name_groups[key].append(cat)
    
    total_duplicates = sum(1 for cats in name_groups.values() if len(cats) > 1)
    children_with_products = sum(1 for cat in all_child_cats if cat.product_set.count() > 0)
    empty_children = total_children - children_with_products
    
    print(f"Total child categories: {total_children}")
    print(f"Remaining duplicate sets: {total_duplicates}")
    print(f"Categories with products: {children_with_products}")
    print(f"Empty categories: {empty_children}")
    
    if total_duplicates == 0:
        print("✅ EXCELLENT: No duplicate categories remain in database!")
    else:
        print("⚠ WARNING: Some duplicates still exist")
    
    # Calculate success rate
    success_rate = (children_with_products / total_children) * 100 if total_children > 0 else 0
    print(f"Database health: {success_rate:.1f}% of categories have products")


if __name__ == "__main__":
    check_multiple_serials()
#!/usr/bin/env python
"""
Check Specific Serial for Duplicates

This script checks if a specific serial has duplicate issues that weren't
caught in the main consolidation.
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


def check_specific_serial(serial):
    """Check a specific serial for duplicate issues"""
    print(f"🔍 CHECKING SERIAL: {serial}")
    print("="*50)
    
    # Get all categories for this serial
    all_categories = Category.objects.filter(slug__contains=f'serial-{serial}')
    child_categories = all_categories.filter(slug__contains='-child-')
    
    print(f"Total categories for this serial: {all_categories.count()}")
    print(f"Child categories: {child_categories.count()}")
    
    if child_categories.count() == 0:
        print("❌ NO CATEGORIES FOUND for this serial!")
        print("This serial may not exist in the production database.")
        return False
    
    # Check for duplicates
    parent_name_groups = defaultdict(list)
    
    for cat in child_categories:
        slug_parts = cat.slug.split('-child-')
        if len(slug_parts) == 2:
            parent_slug_part = slug_parts[0]
            parent_name_groups[(parent_slug_part, cat.name)].append(cat)
    
    duplicates_found = 0
    categories_with_products = 0
    categories_empty = 0
    
    print(f"\n📋 DUPLICATE ANALYSIS:")
    for (parent_slug_part, child_name), categories in parent_name_groups.items():
        if len(categories) > 1:
            duplicates_found += 1
            print(f"\n⚠ DUPLICATE SET #{duplicates_found}: '{child_name}'")
            print(f"   Parent context: {parent_slug_part}")
            
            categories.sort(key=lambda x: x.id)
            original = categories[0]
            duplicates = categories[1:]
            
            print(f"   Original: {original.slug} (ID={original.id}, Products={original.product_set.count()})")
            for dup in duplicates:
                product_count = dup.product_set.count()
                print(f"   Duplicate: {dup.slug} (ID={dup.id}, Products={product_count})")
        else:
            # Single category
            cat = categories[0]
            product_count = cat.product_set.count()
            if product_count > 0:
                categories_with_products += 1
            else:
                categories_empty += 1
    
    print(f"\n📊 SUMMARY:")
    print(f"   Duplicate sets: {duplicates_found}")
    print(f"   Categories with products: {categories_with_products}")
    print(f"   Empty categories: {categories_empty}")
    
    # Check the specific problematic URL
    problem_category = Category.objects.filter(
        slug='serial-LSFAL11A4PA157987-parent-2-child-1'
    ).first()
    
    if problem_category:
        product_count = problem_category.product_set.count()
        print(f"\n🎯 SPECIFIC URL CHECK:")
        print(f"   Category: {problem_category.slug}")
        print(f"   Name: '{problem_category.name}'")
        print(f"   ID: {problem_category.id}")
        print(f"   Products: {product_count}")
        
        if product_count == 0:
            print(f"   ❌ CONFIRMED: This category is empty!")
            
            # Look for duplicates of this specific category
            same_name_cats = Category.objects.filter(
                name=problem_category.name,
                slug__contains=f'serial-{serial}-parent-2'
            ).order_by('slug')
            
            print(f"\n🔍 LOOKING FOR DUPLICATES OF THIS CATEGORY:")
            for cat in same_name_cats:
                product_count = cat.product_set.count()
                print(f"     {cat.slug} (ID={cat.id}, Products={product_count})")
                if product_count > 0:
                    print(f"     ✅ FOUND PRODUCTS HERE! This is where they should be moved from.")
        else:
            print(f"   ✅ This category has products - URL should work!")
    else:
        print(f"\n❌ CATEGORY NOT FOUND: serial-LSFAL11A4PA157987-parent-2-child-1")
        print("This category doesn't exist in the database!")
    
    return duplicates_found > 0


if __name__ == "__main__":
    # Check the specific serial from the problematic URL
    serial = "LSFAL11A4PA157987"
    has_duplicates = check_specific_serial(serial)
    
    if has_duplicates:
        print(f"\n💡 RECOMMENDATION: Run consolidation again to fix this serial")
    else:
        print(f"\n💡 This serial appears clean - the issue may be elsewhere")
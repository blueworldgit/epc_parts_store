#!/usr/bin/env python
"""
Database Consolidation Script for Duplicate Child Categories

This script identifies and consolidates duplicate child categories that were created
during multiple import runs. It moves products from newer duplicate categories
to the original categories and removes the duplicates.

Root Cause: Multiple import runs created duplicate child categories with identical
names but different IDs. Products ended up in the newer categories while URLs
point to the original categories.

Solution: Move all products to original categories and delete duplicates.
"""

import os
import sys
import django
from collections import defaultdict

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from oscar.apps.catalogue.models import Category
from django.db import transaction


def analyze_duplicates():
    """
    Analyze duplicate child categories by finding categories with:
    - Same name
    - Same parent
    - Different IDs/slugs
    """
    print("=== ANALYZING DUPLICATE CHILD CATEGORIES ===\n")
    
    # Get all categories that look like child categories
    child_categories = Category.objects.filter(slug__contains='-child-').order_by('slug')
    
    # Group by parent and name to find duplicates
    parent_name_groups = defaultdict(list)
    
    for cat in child_categories:
        # Extract parent info from slug (e.g., "serial-X-parent-Y" from "serial-X-parent-Y-child-Z")
        slug_parts = cat.slug.split('-child-')
        if len(slug_parts) == 2:
            parent_slug_part = slug_parts[0]  # "serial-X-parent-Y"
            parent_name_groups[(parent_slug_part, cat.name)].append(cat)
    
    duplicates_found = 0
    consolidation_plan = []
    
    for (parent_slug_part, child_name), categories in parent_name_groups.items():
        if len(categories) > 1:
            duplicates_found += 1
            categories.sort(key=lambda x: x.id)  # Sort by ID (original first)
            
            original = categories[0]
            duplicates = categories[1:]
            
            print(f"Duplicate Set #{duplicates_found}:")
            print(f"  Parent: {parent_slug_part}")
            print(f"  Child Name: '{child_name}'")
            print(f"  Original: ID={original.id}, Slug={original.slug}, Products={original.product_set.count()}")
            
            total_products_in_duplicates = 0
            for dup in duplicates:
                product_count = dup.product_set.count()
                total_products_in_duplicates += product_count
                print(f"  Duplicate: ID={dup.id}, Slug={dup.slug}, Products={product_count}")
            
            consolidation_plan.append({
                'original': original,
                'duplicates': duplicates,
                'total_products_to_move': total_products_in_duplicates
            })
            print()
    
    print(f"SUMMARY: Found {duplicates_found} duplicate sets")
    total_products_to_move = sum(item['total_products_to_move'] for item in consolidation_plan)
    print(f"Total products to move: {total_products_to_move}")
    
    return consolidation_plan


def consolidate_duplicates(consolidation_plan, dry_run=True):
    """
    Execute the consolidation plan:
    1. Move products from duplicate categories to original categories
    2. Delete duplicate categories
    """
    if dry_run:
        print("\n=== DRY RUN - NO CHANGES WILL BE MADE ===")
    else:
        print("\n=== EXECUTING CONSOLIDATION ===")
    
    total_moved = 0
    total_deleted = 0
    
    for i, plan_item in enumerate(consolidation_plan, 1):
        original = plan_item['original']
        duplicates = plan_item['duplicates']
        
        print(f"\nConsolidating set {i}: '{original.name}'")
        print(f"  Target: {original.slug} (ID={original.id})")
        
        for dup in duplicates:
            products = dup.product_set.all()
            product_count = products.count()
            
            if product_count > 0:
                print(f"  Moving {product_count} products from {dup.slug} (ID={dup.id})")
                
                if not dry_run:
                    with transaction.atomic():
                        # Move products to original category
                        for product in products:
                            product.categories.remove(dup)
                            product.categories.add(original)
                        
                        print(f"    ✓ Moved {product_count} products")
                        total_moved += product_count
                else:
                    print(f"    [DRY RUN] Would move {product_count} products")
            
            # Delete duplicate category
            if not dry_run:
                with transaction.atomic():
                    dup.delete()
                    print(f"    ✓ Deleted duplicate category {dup.slug}")
                    total_deleted += 1
            else:
                print(f"    [DRY RUN] Would delete duplicate category {dup.slug}")
    
    if not dry_run:
        print(f"\n=== CONSOLIDATION COMPLETE ===")
        print(f"Total products moved: {total_moved}")
        print(f"Total duplicate categories deleted: {total_deleted}")
    else:
        print(f"\n=== DRY RUN COMPLETE ===")
        print(f"Would move {sum(item['total_products_to_move'] for item in consolidation_plan)} products")
        print(f"Would delete {sum(len(item['duplicates']) for item in consolidation_plan)} duplicate categories")


def verify_consolidation():
    """
    Verify that consolidation worked by checking the problematic URL
    """
    print("\n=== VERIFICATION ===")
    
    # Check the specific categories from the problematic URL
    serial = "LSFAL11A4PA157987"
    target_categories = [
        f"serial-{serial}-parent-12-child-1",
        f"serial-{serial}-parent-12-child-2"
    ]
    
    for slug in target_categories:
        category = Category.objects.filter(slug=slug).first()
        if category:
            product_count = category.product_set.count()
            print(f"Category: {slug}")
            print(f"  ID: {category.id}, Products: {product_count}")
            if product_count > 0:
                print(f"  ✓ SUCCESS: Category now has products!")
            else:
                print(f"  ⚠ WARNING: Category still has no products")
        else:
            print(f"Category not found: {slug}")


def main():
    print("DUPLICATE CATEGORY CONSOLIDATION SCRIPT")
    print("=" * 50)
    
    # Step 1: Analyze duplicates
    consolidation_plan = analyze_duplicates()
    
    if not consolidation_plan:
        print("No duplicates found. Database is clean!")
        return
    
    # Step 2: Ask user for confirmation
    print(f"\nFound {len(consolidation_plan)} duplicate sets to consolidate.")
    
    while True:
        choice = input("\nChoose action:\n1. Dry run (preview changes)\n2. Execute consolidation\n3. Exit\nEnter choice (1-3): ").strip()
        
        if choice == "1":
            consolidate_duplicates(consolidation_plan, dry_run=True)
        elif choice == "2":
            print("\n⚠ WARNING: This will permanently modify the database!")
            confirm = input("Type 'CONFIRM' to proceed: ").strip()
            if confirm == "CONFIRM":
                consolidate_duplicates(consolidation_plan, dry_run=False)
                verify_consolidation()
                break
            else:
                print("Operation cancelled.")
        elif choice == "3":
            print("Exiting without changes.")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")


if __name__ == "__main__":
    main()
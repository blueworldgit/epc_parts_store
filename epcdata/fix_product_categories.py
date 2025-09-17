#!/usr/bin/env python
"""
Fix misplaced products in Oscar categories.
This script corrects products that were assigned to wrong categories due to the category lookup bug.
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from oscar.apps.catalogue.models import Category, Product
from motorpartsdata.models import Part, SerialNumber, ParentTitle, ChildTitle
from django.utils import timezone

def fix_misplaced_products():
    print("============================================================")
    print("🔧 FIXING MISPLACED PRODUCTS IN OSCAR CATEGORIES")
    print("============================================================")
    
    corrections_made = 0
    products_checked = 0
    
    # Get all products that have been imported from parts
    all_parts = Part.objects.filter(oscar_imported=True)
    print(f"📦 Checking {all_parts.count()} imported parts...")
    
    for part in all_parts:
        products_checked += 1
        
        try:
            # Find the Oscar product for this part
            oscar_product = Product.objects.get(upc=part.part_number)
            
            # Determine the correct category for this part
            child_title = part.child_title
            parent_title = child_title.parent
            serial_number = parent_title.serial_number
            
            # Build the expected category hierarchy
            correct_category = find_correct_category(serial_number, parent_title, child_title)
            
            if correct_category:
                current_categories = list(oscar_product.categories.all())
                
                # Check if product is in the correct category
                if correct_category not in current_categories:
                    print(f"🔄 Fixing {part.part_number}: {child_title.title}")
                    print(f"   From: {[cat.name for cat in current_categories]}")
                    print(f"   To: {correct_category.name}")
                    
                    # Remove from wrong categories (keep only hierarchical parents)
                    oscar_product.categories.clear()
                    
                    # Add to correct category
                    oscar_product.categories.add(correct_category)
                    
                    corrections_made += 1
                else:
                    if products_checked % 100 == 0:
                        print(f"✅ {part.part_number} already in correct category")
                        
        except Product.DoesNotExist:
            print(f"❌ Product not found in Oscar: {part.part_number}")
            continue
        except Exception as e:
            print(f"❌ Error processing {part.part_number}: {e}")
            continue
            
        if products_checked % 100 == 0:
            print(f"📊 Progress: {products_checked}/{all_parts.count()} checked, {corrections_made} corrected")
    
    print("\n" + "="*60)
    print(f"✅ CORRECTION COMPLETE!")
    print(f"📊 Products checked: {products_checked}")
    print(f"🔧 Corrections made: {corrections_made}")
    print("="*60)

def find_correct_category(serial_number, parent_title, child_title):
    """Find the correct Oscar category for a given part hierarchy"""
    
    # Build the expected category path based on the hierarchy
    # Pattern: Maxus -> Serial LSFAL... -> Parent Title -> Child Title
    
    try:
        # Find vehicle category (Maxus, etc.)
        vehicle_category = Category.objects.filter(name=serial_number.vehicle_brand).first()
        if not vehicle_category:
            print(f"❌ Vehicle category not found: {serial_number.vehicle_brand}")
            return None
        
        # Find serial category 
        serial_category_name = f"Serial {serial_number.serial}"
        serial_category = Category.objects.filter(
            name=serial_category_name,
            depth=vehicle_category.depth + 1
        ).first()
        
        if not serial_category:
            print(f"❌ Serial category not found: {serial_category_name}")
            return None
        
        # Find parent category
        parent_category = Category.objects.filter(
            name=parent_title.title,
            depth=serial_category.depth + 1
        ).first()
        
        if not parent_category:
            print(f"❌ Parent category not found: {parent_title.title}")
            return None
        
        # Find child category (the correct target)
        child_category = Category.objects.filter(
            name=child_title.title,
            depth=parent_category.depth + 1
        ).first()
        
        if not child_category:
            print(f"❌ Child category not found: {child_title.title}")
            return None
            
        return child_category
        
    except Exception as e:
        print(f"❌ Error finding category for {child_title.title}: {e}")
        return None

def preview_corrections():
    """Preview what corrections would be made without actually making them"""
    print("============================================================")
    print("🔍 PREVIEWING CORRECTIONS (DRY RUN)")
    print("============================================================")
    
    corrections_needed = 0
    products_checked = 0
    
    # Sample first 20 parts to preview
    sample_parts = Part.objects.filter(oscar_imported=True)[:20]
    
    for part in sample_parts:
        products_checked += 1
        
        try:
            oscar_product = Product.objects.get(upc=part.part_number)
            child_title = part.child_title
            parent_title = child_title.parent
            serial_number = parent_title.serial_number
            
            correct_category = find_correct_category(serial_number, parent_title, child_title)
            
            if correct_category:
                current_categories = list(oscar_product.categories.all())
                
                if correct_category not in current_categories:
                    print(f"📋 {part.part_number}: {child_title.title}")
                    print(f"   Current: {[cat.name for cat in current_categories]}")
                    print(f"   Should be: {correct_category.name}")
                    print()
                    corrections_needed += 1
                    
        except Product.DoesNotExist:
            continue
        except Exception as e:
            continue
    
    print(f"📊 Sample check: {corrections_needed}/{products_checked} products need correction")
    return corrections_needed > 0

if __name__ == "__main__":
    # First show a preview
    needs_correction = preview_corrections()
    
    if needs_correction:
        print("\n" + "="*60)
        response = input("🔧 Run full correction? (y/N): ").lower().strip()
        if response == 'y':
            fix_misplaced_products()
        else:
            print("👍 Correction cancelled. Run again when ready.")
    else:
        print("✅ No corrections needed!")
#!/usr/bin/env python
"""
Script to create Oscar categories from your existing model structure.
This will create a hierarchical category structure based on:
SerialNumber -> ParentTitle -> ChildTitle
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from oscar.apps.catalogue.models import Category
from motorpartsdata.models import SerialNumber, ParentTitle, ChildTitle

def create_categories():
    """Create Oscar categories from your model hierarchy"""
    
    print("🏗️ Creating Oscar Categories from Motor Parts Data")
    print("=" * 50)
    
    # Clear existing categories if you want a fresh start
    # Category.objects.all().delete()
    
    created_count = 0
    
    # Create categories for SerialNumbers (top level)
    for serial in SerialNumber.objects.all():
        serial_category, created = Category.objects.get_or_create(
            name=f"Serial: {serial.serial}",
            defaults={
                'description': f'Parts for serial number {serial.serial}',
                'slug': f'serial-{serial.serial}',
            }
        )
        if created:
            print(f"📁 Created Serial Category: {serial_category.name}")
            created_count += 1
        
        # Create subcategories for ParentTitles
        for parent in serial.parent_titles.all():
            parent_category, created = Category.objects.get_or_create(
                name=f"{parent.title}",
                defaults={
                    'description': f'Parent category: {parent.title}',
                    'slug': f'parent-{parent.id}',
                }
            )
            if created:
                print(f"  📂 Created Parent Category: {parent_category.name}")
                created_count += 1
            
            # Make parent category a child of serial category
            if parent_category.get_parent() != serial_category:
                parent_category.move(serial_category, 'first-child')
            
            # Create subcategories for ChildTitles
            for child in parent.child_titles.all():
                child_category, created = Category.objects.get_or_create(
                    name=f"{child.title}",
                    defaults={
                        'description': f'Child category: {child.title}',
                        'slug': f'child-{child.id}',
                    }
                )
                if created:
                    print(f"    📄 Created Child Category: {child_category.name}")
                    created_count += 1
                
                # Make child category a child of parent category
                if child_category.get_parent() != parent_category:
                    child_category.move(parent_category, 'first-child')
    
    print("=" * 50)
    print(f"✅ Created {created_count} new categories")
    print(f"📊 Total categories: {Category.objects.count()}")
    
    # Show category tree structure
    print("\n🌳 Category Tree Structure:")
    for root_cat in Category.objects.filter(depth=1):
        print(f"└── {root_cat.name}")
        for child_cat in root_cat.get_children():
            print(f"    └── {child_cat.name}")
            for grandchild_cat in child_cat.get_children():
                print(f"        └── {grandchild_cat.name}")
    
    return created_count

def show_statistics():
    """Show current data statistics"""
    print("\n📈 Current Data Statistics:")
    print(f"   Serial Numbers: {SerialNumber.objects.count()}")
    print(f"   Parent Titles: {ParentTitle.objects.count()}")
    print(f"   Child Titles: {ChildTitle.objects.count()}")
    print(f"   Oscar Categories: {Category.objects.count()}")

if __name__ == "__main__":
    show_statistics()
    created = create_categories()
    
    if created > 0:
        print(f"\n🎉 Successfully created {created} new categories!")
        print("🔗 You can now view them at: http://127.0.0.1:8000/dashboard/catalogue/categories/")
    else:
        print("\n✨ All categories already exist!")

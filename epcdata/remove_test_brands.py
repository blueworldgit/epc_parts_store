#!/usr/bin/env python
"""
Remove the test brands that were created
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from oscar.apps.catalogue.models import Category

def remove_test_brands():
    """Remove the test brands and their children"""
    print("Removing test brands...")
    
    # Brands to remove
    brands_to_remove = ['Iveco', 'LDV', 'Leyland']
    
    for brand_name in brands_to_remove:
        try:
            brand_category = Category.objects.filter(name=brand_name, depth=1).first()
            if brand_category:
                # Get count of children before deletion
                children_count = brand_category.get_descendant_count()
                print(f"🗑️ Removing {brand_name} and {children_count} subcategories...")
                
                # Delete the category and all its children
                brand_category.delete()
                print(f"✅ Deleted {brand_name}")
            else:
                print(f"❌ Brand {brand_name} not found")
        except Exception as e:
            print(f"❌ Error removing {brand_name}: {e}")
    
    print(f"\nRemaining categories: {Category.objects.count()}")
    
    # Show remaining structure
    print("\n🌳 Remaining Category Structure:")
    for brand in Category.objects.filter(depth=1):
        print(f"└── {brand.name} ({brand.get_children().count()} models)")

if __name__ == "__main__":
    remove_test_brands()

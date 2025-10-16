#!/usr/bin/env python
"""
Get all unique category names across all serials
This will help you see what category images you need to prepare
"""
import os
import django
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from oscar.apps.catalogue.models import Category

def get_unique_category_names():
    """Get all unique category names from Oscar categories"""
    
    print("🔍 Fetching all unique category names...")
    
    # Get all categories and extract unique names
    categories = Category.objects.all().values_list('name', flat=True)
    unique_names = set()
    
    for name in categories:
        if name:  # Skip empty/null names
            # Clean up the name - remove technical codes like "JE241A001 - "
            clean_name = name.strip()
            
            # Remove everything before and including " - " (space-dash-space)
            if " - " in clean_name:
                clean_name = clean_name.split(" - ", 1)[1]  # Take everything after first " - "
            
            unique_names.add(clean_name)
    
    # Convert to sorted list
    unique_names = sorted(list(unique_names))
    
    # Generate report
    timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
    filename = f'unique_category_names_{timestamp}.txt'
    
    print(f"📝 Found {len(unique_names)} unique category names")
    print(f"📄 Saving to: {filename}")
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"Unique Category Names Report\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total unique categories: {len(unique_names)}\n")
        f.write("="*80 + "\n\n")
        
        for i, name in enumerate(unique_names, 1):
            f.write(f"{i:3d}. {name}\n")
            print(f"{i:3d}. {name}")
    
    print(f"\n✅ Report saved to: {filename}")
    print(f"\n💡 Next steps:")
    print(f"   1. Review the category names in {filename}")
    print(f"   2. Prepare images with matching names (e.g., 'Airbag.jpg', 'Engine.jpg')")
    print(f"   3. Run the bulk image attachment script")
    
    return filename, len(unique_names)

def get_category_stats():
    """Get some basic statistics about categories"""
    
    total_categories = Category.objects.count()
    categories_with_images = Category.objects.filter(image__isnull=False).exclude(image='').count()
    categories_without_images = total_categories - categories_with_images
    
    print(f"\n📊 Category Statistics:")
    print(f"   Total categories: {total_categories}")
    print(f"   With images: {categories_with_images}")
    print(f"   Without images: {categories_without_images}")
    print(f"   Coverage: {(categories_with_images/total_categories*100):.1f}%")

if __name__ == "__main__":
    print("🏷️  Unique Category Names Generator")
    print("="*50)
    
    try:
        # Get unique names
        filename, count = get_unique_category_names()
        
        # Show statistics
        get_category_stats()
        
        print(f"\n🎯 SUMMARY:")
        print(f"   Report file: {filename}")
        print(f"   Unique category names: {count}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
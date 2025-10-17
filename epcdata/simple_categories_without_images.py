#!/usr/bin/env python
"""
Simple Categories Without Images
Just outputs categories without images, one per line, numbered
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from oscar.apps.catalogue.models import Category

def clean_category_name(name):
    """Clean category name same way as other scripts"""
    if name and " - " in name:
        return name.split(" - ", 1)[1].strip()
    return name.strip() if name else ""

def get_categories_without_images():
    """Get unique category names without images"""
    
    # Get all categories and group by cleaned name
    categories = Category.objects.all()
    category_groups = {}
    
    for cat in categories:
        if cat.name:
            clean_name = clean_category_name(cat.name)
            if clean_name not in category_groups:
                category_groups[clean_name] = []
            category_groups[clean_name].append(cat)
    
    # Find categories without images
    categories_without_images = []
    
    for clean_name, cat_list in category_groups.items():
        has_image = False
        
        for cat in cat_list:
            if cat.image:
                has_image = True
                break
        
        if not has_image:
            categories_without_images.append(clean_name)
    
    # Sort and return
    return sorted(categories_without_images)

if __name__ == "__main__":
    categories_without_images = get_categories_without_images()
    
    for i, category_name in enumerate(categories_without_images, 1):
        print(f"{i}. {category_name}")
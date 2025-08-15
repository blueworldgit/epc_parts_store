#!/usr/bin/env python
"""
Quick script to create basic test categories
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from oscar.apps.catalogue.models import Category
from django.utils.text import slugify

def create_test_categories():
    """Create basic test categories"""
    print("Creating test categories...")
    
    # Create main brands
    brands = ['Maxus', 'Peugeot', 'Iveco', 'LDV', 'Leyland']
    
    for brand_name in brands:
        # Check if brand already exists
        brand_category = Category.objects.filter(name=brand_name, depth=1).first()
        
        if not brand_category:
            # Create root category
            brand_category = Category.add_root(
                name=brand_name,
                description=f'{brand_name} vehicle parts',
                slug=slugify(brand_name),
            )
            print(f"✅ Created brand: {brand_name}")
        else:
            print(f"📦 Brand exists: {brand_name}")
        
        # Create a couple of vehicle models for each brand
        models = ['Model 1', 'Model 2']
        for model_name in models:
            full_model_name = f"{brand_name} {model_name}"
            model_slug = f"{slugify(brand_name)}-{slugify(model_name)}"
            
            # Check if model already exists
            model_category = Category.objects.filter(name=full_model_name).first()
            
            if not model_category:
                # Create as child of brand category
                model_category = brand_category.add_child(
                    name=full_model_name,
                    description=f'Parts for {full_model_name}',
                    slug=model_slug,
                )
                print(f"  ✅ Created model: {full_model_name}")
            else:
                print(f"  📦 Model exists: {full_model_name}")
            
            # Create parts categories
            parts = ['Engine', 'Brakes', 'Suspension']
            for parts_name in parts:
                parts_slug = f"{model_slug}-{slugify(parts_name)}"
                
                # Check if parts category already exists
                parts_category = Category.objects.filter(name=parts_name, slug=parts_slug).first()
                
                if not parts_category:
                    # Create as child of model category
                    parts_category = model_category.add_child(
                        name=parts_name,
                        description=f'{parts_name} for {full_model_name}',
                        slug=parts_slug,
                    )
                    print(f"    ✅ Created parts: {parts_name}")
                else:
                    print(f"    📦 Parts exists: {parts_name}")

    print(f"\nTotal categories: {Category.objects.count()}")

if __name__ == "__main__":
    create_test_categories()

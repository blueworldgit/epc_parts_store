#!/usr/bin/env python
"""
Create sample brand categories for testing the dynamic sidebar
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from oscar.apps.catalogue.models import Category
from django.utils.text import slugify

def create_sample_categories():
    """Create sample brand hierarchy for testing"""
    print("🏗️ Creating Sample Brand Categories")
    print("=" * 50)
    
    # Brand data structure
    brands_data = {
        'Maxus': [
            'eDeliver 3',
            'eDeliver 9', 
            'Deliver 9',
            'V80',
            'T60'
        ],
        'Peugeot': [
            'Boxer',
            'Partner',
            'Expert',
            'Rifter'
        ],
        'Iveco': [
            'Daily',
            'Stralis',
            'Eurocargo'
        ],
        'LDV': [
            'V80',
            'Maxus',
            'Convoy'
        ],
        'Leyland DAF': [
            'LF Series',
            'CF Series', 
            'XF Series'
        ]
    }
    
    # Parts categories that will be under each vehicle model
    parts_categories = [
        'Engine Components',
        'Brake System',
        'Suspension',
        'Electrical',
        'Body Parts',
        'Transmission',
        'Cooling System',
        'Exhaust System',
        'Interior Parts',
        'Filters'
    ]
    
    created_count = 0
    
    for brand_name, vehicle_models in brands_data.items():
        # Create brand category (root level)
        brand_category, created = Category.objects.get_or_create(
            name=brand_name,
            defaults={
                'description': f'{brand_name} vehicle parts and components',
                'slug': slugify(brand_name),
            }
        )
        
        if created:
            print(f"🚗 Created Brand: {brand_category.name}")
            created_count += 1
        else:
            print(f"✅ Brand exists: {brand_category.name}")
        
        # Create vehicle model categories
        for model_name in vehicle_models:
            model_slug = f"{slugify(brand_name)}-{slugify(model_name)}"
            model_category, created = Category.objects.get_or_create(
                name=f"{brand_name} {model_name}",
                defaults={
                    'description': f'Parts for {brand_name} {model_name}',
                    'slug': model_slug,
                }
            )
            
            if created:
                print(f"  📦 Created Model: {model_category.name}")
                created_count += 1
                # Make it a child of brand category
                model_category.move(brand_category, 'last-child')
            else:
                print(f"    ✅ Model exists: {model_category.name}")
                # Ensure it's under the right parent
                if model_category.get_parent() != brand_category:
                    model_category.move(brand_category, 'last-child')
            
            # Create parts categories under each vehicle model
            for parts_name in parts_categories:
                parts_slug = f"{model_slug}-{slugify(parts_name)}"
                parts_category, created = Category.objects.get_or_create(
                    name=parts_name,
                    defaults={
                        'description': f'{parts_name} for {brand_name} {model_name}',
                        'slug': parts_slug,
                    }
                )
                
                if created:
                    print(f"    🔧 Created Parts Category: {parts_category.name}")
                    created_count += 1
                    # Make it a child of model category
                    parts_category.move(model_category, 'last-child')
                else:
                    # Ensure it's under the right parent
                    if parts_category.get_parent() != model_category:
                        parts_category.move(model_category, 'last-child')
    
    print("=" * 50)
    print(f"✅ Created {created_count} new categories")
    print(f"📊 Total categories: {Category.objects.count()}")
    
    # Show the structure
    print("\n🌳 Category Structure:")
    for brand in Category.objects.filter(depth=1):
        print(f"└── {brand.name} ({brand.get_children().count()} models)")
        for model in brand.get_children():
            print(f"    └── {model.name} ({model.get_children().count()} parts categories)")

if __name__ == "__main__":
    create_sample_categories()

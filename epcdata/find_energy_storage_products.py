#!/usr/bin/env python
"""
Find Energy Storage Products Across All Serials

This script finds where Battery & Energy Storage products are located
across all serials to understand the pattern.
"""

import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from oscar.apps.catalogue.models import Category, Product


def find_energy_storage_products():
    """Find where energy storage products are across all serials"""
    print("🔋 FINDING ENERGY STORAGE PRODUCTS ACROSS ALL SERIALS")
    print("="*60)
    
    # Look for categories with energy storage related names
    energy_keywords = [
        'Battery',
        'Energy Storage',
        'PowerInverter',
        'JE843A001',
        'JE844A002',
        'Electrical Energy'
    ]
    
    print("🔍 Searching for categories with energy storage keywords...")
    
    energy_categories = []
    for keyword in energy_keywords:
        cats = Category.objects.filter(name__icontains=keyword)
        for cat in cats:
            if cat not in energy_categories:
                energy_categories.append(cat)
    
    print(f"Found {len(energy_categories)} categories related to energy storage:")
    print()
    
    # Group by serial
    serial_energy_data = {}
    
    for cat in energy_categories:
        if 'serial-' in cat.slug:
            # Extract serial from slug
            parts = cat.slug.split('-')
            if len(parts) >= 3 and parts[0] == 'serial':
                serial_name = parts[1]
                if serial_name not in serial_energy_data:
                    serial_energy_data[serial_name] = []
                
                product_count = cat.product_set.count()
                serial_energy_data[serial_name].append({
                    'category': cat,
                    'products': product_count
                })
    
    # Show results by serial
    print("📊 ENERGY STORAGE BY SERIAL:")
    print("-" * 50)
    
    for serial, categories in serial_energy_data.items():
        total_products = sum(cat_data['products'] for cat_data in categories)
        print(f"\n🔋 Serial: {serial}")
        print(f"   Total energy storage products: {total_products}")
        
        for cat_data in categories:
            cat = cat_data['category']
            products = cat_data['products']
            status = "✅ HAS PRODUCTS" if products > 0 else "❌ EMPTY"
            
            print(f"   {cat.slug}")
            print(f"     Name: '{cat.name}'")
            print(f"     Products: {products} {status}")
            
            # Show sample products if any
            if products > 0:
                sample_products = cat.product_set.all()[:2]
                for product in sample_products:
                    print(f"       • {product.title}")
    
    # Check if there are energy storage products in other categories
    print(f"\n🔍 SEARCHING PRODUCTS BY TITLE...")
    print("-" * 50)
    
    # Search for products with energy storage keywords in title
    energy_products = []
    for keyword in ['battery', 'energy storage', 'inverter', 'electrical']:
        products = Product.objects.filter(title__icontains=keyword)
        for product in products:
            if product not in energy_products:
                energy_products.append(product)
    
    print(f"Found {len(energy_products)} products with energy storage keywords")
    
    # Group these products by their categories
    print("\n📦 WHERE ENERGY STORAGE PRODUCTS ARE ACTUALLY LOCATED:")
    print("-" * 50)
    
    product_locations = {}
    for product in energy_products[:20]:  # Show first 20
        categories = product.categories.all()
        for cat in categories:
            if 'serial-' in cat.slug:
                if cat.slug not in product_locations:
                    product_locations[cat.slug] = []
                product_locations[cat.slug].append(product.title)
    
    for cat_slug, product_titles in product_locations.items():
        print(f"\n{cat_slug}:")
        for title in product_titles[:3]:  # Show first 3 products
            print(f"  • {title}")
        if len(product_titles) > 3:
            print(f"  ... and {len(product_titles) - 3} more")
    
    # Specific check for our problem serial
    print(f"\n🎯 SPECIFIC CHECK FOR LSFAL11A4PA157987:")
    print("-" * 50)
    
    problem_serial = "LSFAL11A4PA157987"
    
    # Check if energy storage products exist anywhere in this serial
    all_cats_for_serial = Category.objects.filter(slug__contains=f'serial-{problem_serial}')
    
    found_energy_products = []
    for cat in all_cats_for_serial:
        products = cat.product_set.filter(title__icontains='battery')
        found_energy_products.extend(products)
        products = cat.product_set.filter(title__icontains='energy')
        found_energy_products.extend(products)
        products = cat.product_set.filter(title__icontains='inverter')
        found_energy_products.extend(products)
    
    # Remove duplicates
    unique_energy_products = list(set(found_energy_products))
    
    if unique_energy_products:
        print(f"✅ FOUND {len(unique_energy_products)} energy storage products for this serial!")
        print("They are located in:")
        
        for product in unique_energy_products[:10]:
            categories = product.categories.filter(slug__contains=f'serial-{problem_serial}')
            for cat in categories:
                print(f"  • {product.title}")
                print(f"    Category: {cat.slug}")
                print(f"    Name: {cat.name}")
                break
    else:
        print("❌ NO energy storage products found for this serial anywhere")
        print("This serial might genuinely not have energy storage products")


if __name__ == "__main__":
    find_energy_storage_products()
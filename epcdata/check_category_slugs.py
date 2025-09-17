#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from oscar.apps.catalogue.models import Category

def main():
    print("=== Checking for categories with expected slugs ===")
    serial = "LSFAL11A4PA157987"
    expected_slugs = [
        f"serial-{serial}-parent-12-child-1",
        f"serial-{serial}-parent-12-child-2", 
        f"serial-{serial}-parent-12-child-3",
        f"serial-{serial}-parent-12-child-4"
    ]
    
    for slug in expected_slugs:
        categories = Category.objects.filter(slug=slug)
        print(f"\nSlug: {slug}")
        print(f"Found: {categories.count()} categories")
        for cat in categories:
            product_count = cat.product_set.count()
            print(f"  ID: {cat.id}, Name: '{cat.name}', Products: {product_count}")
    
    print(f"\n=== All categories for serial {serial} ===")
    all_cats = Category.objects.filter(slug__contains=f"serial-{serial}")
    for cat in all_cats.order_by('slug'):
        product_count = cat.product_set.count()
        print(f"Slug: {cat.slug}")
        print(f"  ID: {cat.id}, Name: '{cat.name}', Products: {product_count}")

if __name__ == "__main__":
    main()
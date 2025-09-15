#!/usr/bin/env python3
"""
Check for duplicate Part records causing MultipleObjectsReturned error
"""
import os
import sys
from pathlib import Path

# Add the project directory to the Python path
project_dir = Path(__file__).parent / "epcdata"
sys.path.insert(0, str(project_dir))

# Load environment
import dotenv
dotenv.load_dotenv()

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')

# Initialize Django
import django
django.setup()

from motorpartsdata.models import Part
from oscar.apps.catalogue.models import Product

def check_duplicate_parts():
    print("🔍 Checking for duplicate Part records...")
    
    # Check specific UPC from the error
    upc = "C00075413"
    print(f"\n📦 Checking UPC: {upc}")
    
    try:
        # This is what's causing the error in the template tag
        parts = Part.objects.filter(part_number=upc)
        count = parts.count()
        
        print(f"Found {count} Part records with part_number='{upc}'")
        
        if count > 1:
            print("\n🚨 DUPLICATE PARTS FOUND:")
            for i, part in enumerate(parts, 1):
                print(f"  {i}. Part ID: {part.id}")
                print(f"     Part Number: {part.part_number}")
                print(f"     Usage Name: {part.usage_name}")
                print(f"     Child Title: {part.child_title}")
                print(f"     Call Out Order: {part.call_out_order}")
                print()
        
        # Check if there's an Oscar product with this UPC
        try:
            oscar_product = Product.objects.get(upc=upc)
            print(f"✅ Oscar Product found: {oscar_product.title}")
        except Product.DoesNotExist:
            print("❌ No Oscar Product found with this UPC")
        except Product.MultipleObjectsReturned:
            oscar_products = Product.objects.filter(upc=upc)
            print(f"🚨 Multiple Oscar Products found: {oscar_products.count()}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Check for other duplicates
    print("\n🔍 Checking for other duplicate part numbers...")
    
    # Find all part numbers with duplicates
    from django.db.models import Count
    duplicates = Part.objects.values('part_number').annotate(
        count=Count('part_number')
    ).filter(count__gt=1).order_by('-count')
    
    print(f"Found {duplicates.count()} part numbers with duplicates:")
    
    for dup in duplicates[:10]:  # Show first 10
        part_number = dup['part_number']
        count = dup['count']
        print(f"  - {part_number}: {count} duplicates")
        
        # Show details for first few
        if count <= 5:
            parts = Part.objects.filter(part_number=part_number)
            for part in parts:
                print(f"    ID: {part.id}, Child: {part.child_title}, Usage: {part.usage_name}")

if __name__ == "__main__":
    check_duplicate_parts()
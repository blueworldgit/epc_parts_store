#!/usr/bin/env python
import os
import sys
import django

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from oscar.apps.catalogue.models import Category, Product
from motorpartsdata.models import Part, SerialNumber

def debug_category_structure():
    print("============================================================")
    print("🔍 CATEGORY STRUCTURE DIAGNOSTIC")
    print("============================================================")
    
    # Find LSFAL11A4PA157987 related categories
    lsfal_categories = Category.objects.filter(name__contains="LSFAL11A4PA157987").order_by('depth', 'name')
    
    print(f"📂 Categories containing 'LSFAL11A4PA157987': {lsfal_categories.count()}")
    for cat in lsfal_categories:
        print(f"   - {cat.name} (depth: {cat.depth}, products: {cat.product_set.count()})")
        print(f"     URL: {cat.get_absolute_url()}")
        if cat.get_parent():
            print(f"     Parent: {cat.get_parent().name}")
        print()
    
    # Check the specific serial number in source data
    print("🔍 SOURCE DATA CHECK:")
    try:
        serial = SerialNumber.objects.get(serial="LSFAL11A4PA157987")
        print(f"✅ Serial found: {serial.serial}")
        
        # Parts are linked through: Part -> ChildTitle -> ParentTitle -> SerialNumber
        parts = Part.objects.filter(child_title__parent__serial_number=serial)
        print(f"📋 Total parts for this serial: {parts.count()}")
        
        # Check specific parent/child combinations
        # Note: parent_number and child_number are NOT direct fields on Part
        # We need to look at the actual parent and child title names
        parent_titles = serial.parent_titles.all()
        print(f"📋 Parent titles for this serial: {parent_titles.count()}")
        for parent in parent_titles[:3]:
            print(f"   - {parent.title}")
            child_titles = parent.child_titles.all()
            for child in child_titles[:3]:
                print(f"     └─ {child.title} ({child.parts.count()} parts)")
        
        if parts.exists():
            print("   Sample parts:")
            for part in parts[:5]:
                print(f"   - {part.part_number}: {part.usage_name}")
                print(f"     Parent: {part.child_title.parent.title}")
                print(f"     Child: {part.child_title.title}")
                # Check if imported to Oscar
                try:
                    oscar_product = Product.objects.get(upc=part.part_number)
                    categories = oscar_product.categories.all()
                    print(f"     ✅ In Oscar, categories: {[cat.name for cat in categories]}")
                except Product.DoesNotExist:
                    print(f"     ❌ Not in Oscar yet")
        
    except SerialNumber.DoesNotExist:
        print("❌ Serial number LSFAL11A4PA157987 not found in source data")
    
    print()
    print("🔍 CHECKING MAXUS CATEGORY STRUCTURE:")
    maxus_cats = Category.objects.filter(name__icontains="maxus").order_by('depth', 'name')
    for cat in maxus_cats[:10]:
        print(f"   - {cat.name} (depth: {cat.depth}, products: {cat.product_set.count()})")

if __name__ == "__main__":
    debug_category_structure()
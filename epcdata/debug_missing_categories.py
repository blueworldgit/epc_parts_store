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
from motorpartsdata.models import Part, SerialNumber, ParentTitle, ChildTitle

def debug_missing_categories():
    print("============================================================")
    print("🔍 MISSING CATEGORIES DEBUG - LSFAL11A4PA157987")
    print("============================================================")
    
    # Get the serial
    try:
        serial = SerialNumber.objects.get(serial="LSFAL11A4PA157987")
        print(f"✅ Serial found: {serial.serial}")
        
        # Get all parent titles for this serial
        parent_titles = serial.parent_titles.all()
        print(f"📂 Parent titles in database: {parent_titles.count()}")
        
        for parent in parent_titles:
            print(f"\n📁 Parent: {parent.title}")
            child_titles = parent.child_titles.all()
            print(f"   Child titles: {child_titles.count()}")
            
            for child in child_titles:
                parts_count = child.parts.count()
                print(f"   └─ {child.title} ({parts_count} parts)")
                
                # Check if this child has been imported to Oscar
                if parts_count > 0:
                    sample_part = child.parts.first()
                    try:
                        oscar_product = Product.objects.get(upc=sample_part.part_number)
                        categories = oscar_product.categories.all()
                        print(f"      ✅ In Oscar: {[cat.name for cat in categories]}")
                    except Product.DoesNotExist:
                        print(f"      ❌ NOT in Oscar yet")
        
        print("\n" + "="*60)
        print("🔍 CHECKING FOR CHARGING & ENERGY STORAGE:")
        
        # Look for charging/energy storage specifically
        charging_parent = parent_titles.filter(title__icontains="charging").first()
        if charging_parent:
            print(f"✅ Found charging parent: {charging_parent.title}")
            charging_children = charging_parent.child_titles.all()
            for child in charging_children:
                parts_count = child.parts.count()
                print(f"   └─ {child.title} ({parts_count} parts)")
        else:
            print("❌ No 'charging' parent title found")
            print("   Available parent titles:")
            for parent in parent_titles:
                if "charg" in parent.title.lower() or "energy" in parent.title.lower() or "battery" in parent.title.lower():
                    print(f"   - {parent.title}")
        
        print("\n" + "="*60)
        print("🔍 SEARCHING FOR BATTERY/ENERGY KEYWORDS:")
        
        # Search all child titles for battery/energy keywords
        all_children = ChildTitle.objects.filter(parent__serial_number=serial)
        battery_children = all_children.filter(title__icontains="battery")
        energy_children = all_children.filter(title__icontains="energy")
        
        print(f"🔋 Children with 'battery': {battery_children.count()}")
        for child in battery_children:
            print(f"   - {child.title} (parent: {child.parent.title}, parts: {child.parts.count()})")
        
        print(f"⚡ Children with 'energy': {energy_children.count()}")
        for child in energy_children:
            print(f"   - {child.title} (parent: {child.parent.title}, parts: {child.parts.count()})")
        
        print("\n" + "="*60)
        print("🔍 OSCAR CATEGORIES WITH BATTERY/ENERGY:")
        
        # Check Oscar categories
        oscar_battery_cats = Category.objects.filter(name__icontains="battery")
        oscar_energy_cats = Category.objects.filter(name__icontains="energy")
        
        print(f"🔋 Oscar categories with 'battery': {oscar_battery_cats.count()}")
        for cat in oscar_battery_cats:
            print(f"   - {cat.name} ({cat.product_set.count()} products)")
            
        print(f"⚡ Oscar categories with 'energy': {oscar_energy_cats.count()}")
        for cat in oscar_energy_cats:
            print(f"   - {cat.name} ({cat.product_set.count()} products)")
            
    except SerialNumber.DoesNotExist:
        print("❌ Serial LSFAL11A4PA157987 not found")

if __name__ == "__main__":
    debug_missing_categories()
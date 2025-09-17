#!/usr/bin/env python
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from oscar.apps.catalogue.models import Category, Product
from motorpartsdata.models import Part

def check_misplaced_products():
    print("============================================================")
    print("🔍 CHECKING PRODUCTS IN PARENT VS CHILD CATEGORIES")
    print("============================================================")
    
    # Find the parent category with products
    parent_cat = Category.objects.filter(
        name="Charging & Energystorage",
        slug="serial-LSFAL11A4PA157987-parent-12"
    ).first()
    
    if parent_cat:
        print(f"📁 Parent Category: {parent_cat.name}")
        print(f"   Products: {parent_cat.product_set.count()}")
        print(f"   URL: {parent_cat.get_absolute_url()}")
        
        print(f"\n📦 Products in parent category:")
        for product in parent_cat.product_set.all():
            print(f"   - {product.upc}: {product.title}")
            
            # Try to find the corresponding Part in motorpartsdata
            try:
                part = Part.objects.filter(part_number=product.upc).first()
                if part:
                    child_title = part.child_title
                    parent_title = child_title.parent
                    
                    print(f"     Source: {parent_title.title} -> {child_title.title}")
                    print(f"     Should be in child category: {child_title.title}")
                    
                    # Find the correct child category
                    correct_child_cat = Category.objects.filter(
                        name=child_title.title,
                        slug__contains="parent-12-child"
                    ).first()
                    
                    if correct_child_cat:
                        print(f"     Correct category exists: {correct_child_cat.name}")
                        print(f"     Correct URL: {correct_child_cat.get_absolute_url()}")
                        
                        # Check if product is also in correct category
                        if product in correct_child_cat.product_set.all():
                            print(f"     ✅ Product IS in correct child category too")
                        else:
                            print(f"     ❌ Product NOT in correct child category")
                    else:
                        print(f"     ❌ Correct child category not found")
                else:
                    print(f"     ❌ Part not found in EPC data")
            except Exception as e:
                print(f"     ❌ Error retrieving part: {e}")
                    
                print()
                
            except Part.DoesNotExist:
                print(f"     ❌ Part not found in motorpartsdata")
                print()
    
    # Check child categories
    print("\n" + "="*60)
    print("🔍 CHECKING CHILD CATEGORIES")
    print("="*60)
    
    child_cats = Category.objects.filter(
        slug__regex=r"serial-LSFAL11A4PA157987-parent-12-child-[12]$"
    )
    
    for child_cat in child_cats:
        print(f"\n📁 Child Category: {child_cat.name}")
        print(f"   Slug: {child_cat.slug}")
        print(f"   Products: {child_cat.product_set.count()}")
        print(f"   URL: {child_cat.get_absolute_url()}")
        
        if child_cat.product_set.count() > 0:
            print(f"   Products:")
            for product in child_cat.product_set.all():
                print(f"     - {product.upc}: {product.title}")

if __name__ == "__main__":
    check_misplaced_products()
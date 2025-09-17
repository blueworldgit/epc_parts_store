#!/usr/bin/env python
"""
Diagnostic script to check call-out data for part C00254952
Compares local vs server data for debugging
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from motorpartsdata.models import Part, SerialNumber, ParentTitle, ChildTitle
from oscar.apps.catalogue.models import Product, ProductAttribute, ProductAttributeValue

def main():
    part_number = "C00254952"
    
    print("=" * 80)
    print(f"🔍 DIAGNOSTIC REPORT FOR PART: {part_number}")
    print("=" * 80)
    print()
    
    # 1. Check motorpartsdata Part model
    print("📋 1. CHECKING MOTORPARTSDATA PART MODEL")
    print("-" * 50)
    
    parts = Part.objects.filter(part_number=part_number)
    print(f"Found {parts.count()} Part records with part_number '{part_number}'")
    
    if parts.exists():
        for i, part in enumerate(parts, 1):
            print(f"\n   Part #{i}:")
            print(f"   - ID: {part.id}")
            print(f"   - Part Number: {part.part_number}")
            print(f"   - Call-out Order: {part.call_out_order}")
            print(f"   - Usage Name: {part.usage_name}")
            print(f"   - LR: {part.lr}")
            print(f"   - Remark: {part.remark}")
            print(f"   - Oscar Imported: {part.oscar_imported}")
            print(f"   - Oscar Imported At: {part.oscar_imported_at}")
            
            # Show parent/child hierarchy
            child_title = part.child_title
            parent_title = child_title.parent
            serial_number = parent_title.serial_number
            
            print(f"   - Serial: {serial_number.serial}")
            print(f"   - Parent Title: {parent_title.title}")
            print(f"   - Child Title: {child_title.title}")
    else:
        print("   ❌ No Part records found!")
    
    print()
    
    # 2. Check Oscar Product model
    print("🛒 2. CHECKING OSCAR PRODUCT MODEL")
    print("-" * 50)
    
    products = Product.objects.filter(upc=part_number)
    print(f"Found {products.count()} Product records with UPC '{part_number}'")
    
    if products.exists():
        for i, product in enumerate(products, 1):
            print(f"\n   Product #{i}:")
            print(f"   - ID: {product.id}")
            print(f"   - UPC: {product.upc}")
            print(f"   - Title: {product.title}")
            print(f"   - Structure: {product.structure}")
            print(f"   - Date Created: {product.date_created}")
            print(f"   - Date Updated: {product.date_updated}")
            
            # Show categories
            categories = product.categories.all()
            print(f"   - Categories: {[cat.name for cat in categories]}")
    else:
        print("   ❌ No Product records found!")
    
    print()
    
    # 3. Check ProductAttribute setup
    print("🏷️  3. CHECKING PRODUCTATTRIBUTE SETUP")
    print("-" * 50)
    
    call_out_attr = ProductAttribute.objects.filter(code='call_out_order').first()
    if call_out_attr:
        print("   ✅ call_out_order attribute exists:")
        print(f"   - ID: {call_out_attr.id}")
        print(f"   - Name: {call_out_attr.name}")
        print(f"   - Type: {call_out_attr.type}")
        print(f"   - Code: {call_out_attr.code}")
    else:
        print("   ❌ call_out_order ProductAttribute not found!")
    
    orientation_attr = ProductAttribute.objects.filter(code='orientation').first()
    if orientation_attr:
        print("   ✅ orientation attribute exists:")
        print(f"   - ID: {orientation_attr.id}")
        print(f"   - Name: {orientation_attr.name}")
        print(f"   - Type: {orientation_attr.type}")
        print(f"   - Code: {orientation_attr.code}")
    else:
        print("   ❌ orientation ProductAttribute not found!")
    
    print()
    
    # 4. Check ProductAttributeValue for this specific product
    print("💎 4. CHECKING PRODUCTATTRIBUTEVALUE DATA")
    print("-" * 50)
    
    if products.exists():
        product = products.first()
        
        # Check call_out_order value
        if call_out_attr:
            call_out_value = ProductAttributeValue.objects.filter(
                product=product,
                attribute=call_out_attr
            ).first()
            
            if call_out_value:
                print("   ✅ call_out_order value found:")
                print(f"   - Product: {call_out_value.product.upc}")
                print(f"   - Attribute: {call_out_value.attribute.code}")
                print(f"   - Value: '{call_out_value.value_text}'")
                print(f"   - Value Integer: {call_out_value.value_integer}")
            else:
                print("   ❌ No call_out_order ProductAttributeValue found!")
        
        # Check orientation value
        if orientation_attr:
            orientation_value = ProductAttributeValue.objects.filter(
                product=product,
                attribute=orientation_attr
            ).first()
            
            if orientation_value:
                print("   ✅ orientation value found:")
                print(f"   - Product: {orientation_value.product.upc}")
                print(f"   - Attribute: {orientation_value.attribute.code}")
                print(f"   - Value: '{orientation_value.value_text}'")
            else:
                print("   ❌ No orientation ProductAttributeValue found!")
        
        # Show ALL ProductAttributeValues for this product
        all_values = ProductAttributeValue.objects.filter(product=product)
        print(f"\n   📊 All ProductAttributeValues for this product ({all_values.count()}):")
        for value in all_values:
            print(f"   - {value.attribute.code}: '{value.value_text}' (int: {value.value_integer})")
    
    print()
    
    # 5. Template tag simulation
    print("🎨 5. SIMULATING TEMPLATE TAG BEHAVIOR")
    print("-" * 50)
    
    if products.exists():
        product = products.first()
        
        # Simulate get_call_out_order template tag
        try:
            call_out_attr = ProductAttribute.objects.get(code='call_out_order')
            call_out_value = ProductAttributeValue.objects.filter(
                product=product,
                attribute=call_out_attr
            ).first()
            
            if call_out_value and call_out_value.value_text:
                print(f"   ✅ Template tag would return: 'This is part {call_out_value.value_text} from the diagram'")
            else:
                print("   ❌ Template tag would return empty (no value_text)")
                
        except ProductAttribute.DoesNotExist:
            print("   ❌ Template tag would fail (attribute doesn't exist)")
        except Exception as e:
            print(f"   ❌ Template tag would error: {e}")
    
    print()
    
    # 6. Check for data differences
    print("🔄 6. DATA INTEGRITY CHECK")
    print("-" * 50)
    
    if parts.exists() and products.exists():
        part = parts.first()
        product = products.first()
        
        # Compare call-out values
        expected_call_out = str(part.call_out_order)
        
        if call_out_attr:
            call_out_value = ProductAttributeValue.objects.filter(
                product=product,
                attribute=call_out_attr
            ).first()
            
            actual_call_out = call_out_value.value_text if call_out_value else None
            
            print(f"   Expected call-out (from Part): '{expected_call_out}'")
            print(f"   Actual call-out (from Oscar): '{actual_call_out}'")
            
            if expected_call_out == actual_call_out:
                print("   ✅ Call-out values match!")
            else:
                print("   ❌ Call-out values DO NOT match!")
                print(f"   💡 This explains why it's not showing on server!")
    
    print()
    print("=" * 80)
    print("🎯 SUMMARY:")
    print("If call-out is not showing, check:")
    print("1. ProductAttribute 'call_out_order' exists")
    print("2. ProductAttributeValue exists for this product")
    print("3. value_text field contains the expected call-out number")
    print("4. Template is loading the correct template tags")
    print("=" * 80)

if __name__ == "__main__":
    main()
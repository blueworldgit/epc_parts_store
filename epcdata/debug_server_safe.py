#!/usr/bin/env python
"""
Server-safe diagnostic script that doesn't use the new oscar_imported fields
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from oscar.apps.catalogue.models import Product, ProductAttribute, ProductAttributeValue

def main():
    part_number = "C00254952"
    
    print("=" * 80)
    print(f"🌐 SERVER DIAGNOSTIC FOR PART: {part_number} (SAFE VERSION)")
    print("=" * 80)
    print()
    
    # Check Oscar Product model only
    print("🛒 CHECKING OSCAR PRODUCT MODEL")
    print("-" * 50)
    
    products = Product.objects.filter(upc=part_number)
    print(f"Found {products.count()} Product records with UPC '{part_number}'")
    
    if products.exists():
        product = products.first()
        print(f"✅ Product found:")
        print(f"   - ID: {product.id}")
        print(f"   - UPC: {product.upc}")
        print(f"   - Title: {product.title}")
        print()
        
        # Check ProductAttribute setup
        print("🏷️  CHECKING PRODUCTATTRIBUTE SETUP")
        print("-" * 50)
        
        call_out_attr = ProductAttribute.objects.filter(code='call_out_order').first()
        if call_out_attr:
            print("✅ call_out_order attribute exists")
            
            # Check ProductAttributeValue
            call_out_value = ProductAttributeValue.objects.filter(
                product=product,
                attribute=call_out_attr
            ).first()
            
            if call_out_value:
                print(f"✅ ProductAttributeValue exists: '{call_out_value.value_text}'")
            else:
                print("❌ No ProductAttributeValue found for call_out_order!")
        else:
            print("❌ call_out_order ProductAttribute not found!")
        
        print()
        
        # Template tag test
        print("🎨 TEMPLATE TAG TEST")
        print("-" * 30)
        
        try:
            from motorpartsdata.templatetags.parts_tags import get_call_out_order
            result = get_call_out_order(product)
            print(f"✅ Template tag result: '{result}'")
            
            if result:
                print(f"✅ Full display would be: 'This is part {result} from the diagram'")
            else:
                print("❌ Template tag returned empty result")
                
        except Exception as e:
            print(f"❌ Template tag failed: {e}")
        
    else:
        print("❌ No Product found!")
    
    print()
    print("=" * 80)

if __name__ == "__main__":
    main()
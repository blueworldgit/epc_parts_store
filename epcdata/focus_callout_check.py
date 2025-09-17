#!/usr/bin/env python
"""
Temporary server diagnostic that avoids the new Part fields entirely
Focus only on the call-out display issue
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
    
    print("=" * 60)
    print(f"🎯 CALL-OUT DIAGNOSTIC FOR: {part_number}")
    print("=" * 60)
    
    # Check Oscar Product
    product = Product.objects.filter(upc=part_number).first()
    
    if not product:
        print("❌ Product not found in Oscar!")
        return
    
    print(f"✅ Product found: {product.title}")
    
    # Check call-out attribute
    try:
        call_out_attr = ProductAttribute.objects.get(code='call_out_order')
        print("✅ call_out_order attribute exists")
        
        # Check the value
        value_obj = ProductAttributeValue.objects.filter(
            product=product,
            attribute=call_out_attr
        ).first()
        
        if value_obj:
            print(f"✅ Call-out value: '{value_obj.value_text}'")
            
            # Test template tag
            try:
                from motorpartsdata.templatetags.parts_tags import get_call_out_order
                result = get_call_out_order(product)
                print(f"✅ Template tag works: '{result}'")
                
                if result:
                    print(f"✅ Would display: 'This is part {result} from the diagram'")
                else:
                    print("❌ Template tag returns empty")
                    
            except Exception as e:
                print(f"❌ Template tag error: {e}")
        else:
            print("❌ No call-out value found!")
            
    except ProductAttribute.DoesNotExist:
        print("❌ call_out_order attribute missing!")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
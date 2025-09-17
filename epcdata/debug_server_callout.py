#!/usr/bin/env python
"""
Server-specific diagnostic script for call-out display issues
Run this on your server to compare with local results
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from motorpartsdata.models import Part
from oscar.apps.catalogue.models import Product, ProductAttribute, ProductAttributeValue
from django.template import Template, Context
from django.template.loader import get_template

def main():
    part_number = "C00254952"
    
    print("=" * 80)
    print(f"🌐 SERVER DIAGNOSTIC FOR PART: {part_number}")
    print("=" * 80)
    print()
    
    # Check environment
    print("🖥️  ENVIRONMENT CHECK")
    print("-" * 30)
    print(f"Django version: {django.get_version()}")
    print(f"Python version: {sys.version}")
    print(f"Current working directory: {os.getcwd()}")
    print()
    
    # Quick data check
    print("📊 QUICK DATA CHECK")
    print("-" * 30)
    
    # Check if part exists
    part = Part.objects.filter(part_number=part_number).first()
    product = Product.objects.filter(upc=part_number).first()
    call_out_attr = ProductAttribute.objects.filter(code='call_out_order').first()
    
    print(f"Part exists: {'✅' if part else '❌'}")
    print(f"Product exists: {'✅' if product else '❌'}")
    print(f"call_out_order attribute exists: {'✅' if call_out_attr else '❌'}")
    
    if part:
        print(f"Part call_out_order: {part.call_out_order}")
    
    if product and call_out_attr:
        call_out_value = ProductAttributeValue.objects.filter(
            product=product,
            attribute=call_out_attr
        ).first()
        print(f"ProductAttributeValue exists: {'✅' if call_out_value else '❌'}")
        if call_out_value:
            print(f"Value: '{call_out_value.value_text}'")
    
    print()
    
    # Template tags check
    print("🎨 TEMPLATE TAGS CHECK")
    print("-" * 30)
    
    try:
        # Try to import template tags
        from motorpartsdata.templatetags.parts_tags import get_call_out_order
        print("✅ Template tags imported successfully")
        
        if product:
            # Test the template tag directly
            result = get_call_out_order(product)
            print(f"get_call_out_order result: '{result}'")
        
    except ImportError as e:
        print(f"❌ Failed to import template tags: {e}")
    except Exception as e:
        print(f"❌ Error testing template tag: {e}")
    
    print()
    
    # Template rendering test
    print("🖼️  TEMPLATE RENDERING TEST")
    print("-" * 30)
    
    if product:
        try:
            # Create a simple template to test
            template_string = """
            {% load parts_tags %}
            Call-out: {{ product|get_call_out_order }}
            Full text: {% if product|get_call_out_order %}This is part {{ product|get_call_out_order }} from the diagram{% endif %}
            """
            
            template = Template(template_string)
            context = Context({'product': product})
            result = template.render(context)
            
            print("✅ Template rendered successfully:")
            print(result.strip())
            
        except Exception as e:
            print(f"❌ Template rendering failed: {e}")
    
    print()
    
    # Database queries debug
    print("🗄️  DATABASE QUERIES DEBUG")
    print("-" * 30)
    
    if product and call_out_attr:
        # Raw SQL to check the data
        from django.db import connection
        
        cursor = connection.cursor()
        cursor.execute("""
            SELECT pav.value_text, pav.value_integer, pa.code, pa.name
            FROM catalogue_productattributevalue pav
            JOIN catalogue_productattribute pa ON pav.attribute_id = pa.id
            WHERE pav.product_id = %s AND pa.code = 'call_out_order'
        """, [product.id])
        
        results = cursor.fetchall()
        print(f"Raw SQL results: {results}")
        
        # Check all attributes for this product
        cursor.execute("""
            SELECT pa.code, pa.name, pav.value_text, pav.value_integer
            FROM catalogue_productattributevalue pav
            JOIN catalogue_productattribute pa ON pav.attribute_id = pa.id
            WHERE pav.product_id = %s
        """, [product.id])
        
        all_attrs = cursor.fetchall()
        print(f"All attributes for product: {all_attrs}")
    
    print()
    
    # Check template file existence
    print("📁 TEMPLATE FILES CHECK")
    print("-" * 30)
    
    template_paths = [
        'oscar/catalogue/detail.html',
        'catalogue/detail.html',
        'motorpartsdata/templatetags/parts_tags.py'
    ]
    
    for path in template_paths:
        try:
            if path.endswith('.py'):
                # Check Python file
                import importlib.util
                full_path = os.path.join(os.getcwd(), 'motorpartsdata', 'templatetags', 'parts_tags.py')
                exists = os.path.exists(full_path)
                print(f"{path}: {'✅' if exists else '❌'}")
            else:
                # Check template file
                template = get_template(path)
                print(f"{path}: ✅ (found)")
        except Exception as e:
            print(f"{path}: ❌ ({e})")
    
    print()
    print("=" * 80)
    print("🎯 NEXT STEPS:")
    print("1. Compare this output with your local results")
    print("2. Check if template tags are properly loaded in templates")
    print("3. Verify Oscar template inheritance is working")
    print("4. Check for any server-specific template caching issues")
    print("=" * 80)

if __name__ == "__main__":
    main()
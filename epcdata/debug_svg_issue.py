#!/usr/bin/env python
"""
Debug script to investigate SVG display issue for part C00212072
"""
import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from motorpartsdata.models import Part
from oscar.apps.catalogue.models import Product
from motorpartsdata.templatetags.parts_tags import get_product_svg

def debug_part_svg(part_number_to_check="C00212072"):
    """Debug SVG display for a specific part"""
    print(f"🔍 Debugging SVG for part: {part_number_to_check}")
    print("="*60)
    
    # 1. Check if part exists in motorpartsdata
    print("1. Checking Part in motorpartsdata...")
    try:
        # Check if there are multiple parts with same number
        parts = Part.objects.select_related('child_title').filter(part_number=part_number_to_check)
        print(f"   📊 Found {parts.count()} parts with number {part_number_to_check}")
        
        for i, part in enumerate(parts, 1):
            print(f"\n   Part #{i}:")
            print(f"   ✅ Part found: {part.part_number}")
            print(f"   📝 Usage name: {part.usage_name}")
            print(f"   🔗 Child title exists: {bool(part.child_title)}")
            print(f"   🆔 Part ID: {part.id}")
            
            if part.child_title:
                print(f"   📋 Child title: {part.child_title.title}")
                print(f"   🔗 Child title ID: {part.child_title.id}")
                print(f"   🖼️ SVG code exists: {bool(part.child_title.svg_code)}")
                if part.child_title.svg_code:
                    print(f"   📏 SVG length: {len(part.child_title.svg_code)} characters")
                    print(f"   👀 SVG preview: {part.child_title.svg_code[:100]}...")
                else:
                    print("   ❌ SVG code is empty or None")
            else:
                print("   ❌ No child title associated with this part")
        
        if parts.count() == 0:
            print(f"   ❌ Part {part_number_to_check} not found in database")
            return
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    print("\n" + "="*60)
    
    # 2. Check Oscar product
    print("2. Checking Oscar Product...")
    upc_variants = [part_number_to_check, f"EPC-{part_number_to_check}"]
    product_found = None
    
    for upc in upc_variants:
        try:
            product = Product.objects.get(upc=upc)
            product_found = product
            print(f"   ✅ Product found with UPC: {upc}")
            print(f"   📝 Title: {product.title}")
            print(f"   🔗 Slug: {product.slug}")
            print(f"   🆔 ID: {product.id}")
            break
        except Product.DoesNotExist:
            print(f"   ❌ No product found with UPC: {upc}")
    
    if not product_found:
        print("   ❌ No Oscar product found for this part")
        return
    
    print("\n" + "="*60)
    
    # 3. Test template tag
    print("3. Testing Template Tag...")
    svg_content = get_product_svg(product_found)
    
    if svg_content:
        print(f"   ✅ Template tag SUCCESS!")
        print(f"   📏 SVG length: {len(svg_content)} characters")
        print(f"   👀 SVG preview: {svg_content[:100]}...")
    else:
        print("   ❌ Template tag returned None")
        
        # Debug template tag logic
        print("\n   🔍 Debugging template tag logic:")
        extracted_part_number = product_found.upc
        if extracted_part_number.startswith('EPC-'):
            extracted_part_number = extracted_part_number[4:]
            
        print(f"   📝 Original UPC: {product_found.upc}")
        print(f"   📝 Extracted part number: {extracted_part_number}")
        
        # Check if the extracted part number finds the part
        try:
            template_part = Part.objects.select_related('child_title').get(part_number=extracted_part_number)
            print(f"   ✅ Template found part: {template_part.part_number}")
            
            if template_part.child_title and template_part.child_title.svg_code:
                print(f"   ✅ Template found SVG: {len(template_part.child_title.svg_code)} chars")
                print("   ❓ But template tag still returned None - check template tag code!")
            else:
                print("   ❌ Template found part but no SVG")
                
        except Part.DoesNotExist:
            print(f"   ❌ Template couldn't find part: {extracted_part_number}")
    
    print("\n" + "="*60)
    
    # 4. Check for common issues
    print("4. Checking for Common Issues...")
    
    # Check if there are multiple parts with similar names
    similar_parts = Part.objects.filter(part_number__icontains=part_number_to_check[:5])
    print(f"   📊 Similar parts found: {similar_parts.count()}")
    
    for similar_part in similar_parts[:5]:  # Show first 5
        print(f"      - {similar_part.part_number}")
    
    # Check if there are any parts with SVG for comparison
    parts_with_svg = Part.objects.select_related('child_title').filter(
        child_title__svg_code__isnull=False
    ).exclude(child_title__svg_code='')[:3]
    
    print(f"   📊 Parts with SVG (for comparison): {parts_with_svg.count()}")
    for svg_part in parts_with_svg:
        print(f"      - {svg_part.part_number} (SVG: {len(svg_part.child_title.svg_code)} chars)")

if __name__ == "__main__":
    debug_part_svg("C00212072")

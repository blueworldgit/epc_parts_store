#!/usr/bin/env python
"""
Create a simple test to check SVG rendering
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

def create_svg_test_file():
    """Create a test HTML file to check SVG rendering"""
    
    # Get the product
    try:
        product = Product.objects.get(upc="EPC-C00212072")
        svg_content = get_product_svg(product)
        
        if svg_content:
            # Clean up the SVG content
            svg_content = svg_content.strip()
            
            # Create a simple HTML test file
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>SVG Test for {product.title}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
        }}
        .svg-container {{
            border: 2px solid #007bff;
            padding: 20px;
            margin: 20px 0;
            background: #f8f9fa;
        }}
        .info {{
            background: #d4edda;
            border: 1px solid #c3e6cb;
            padding: 10px;
            margin: 10px 0;
            border-radius: 4px;
        }}
        .warning {{
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            padding: 10px;
            margin: 10px 0;
            border-radius: 4px;
        }}
    </style>
</head>
<body>
    <h1>SVG Test for Part: {product.upc}</h1>
    <h2>Product: {product.title}</h2>
    
    <div class="info">
        <strong>✅ SVG Found!</strong><br>
        Length: {len(svg_content)} characters<br>
        First 100 characters: <code>{svg_content[:100]}...</code>
    </div>
    
    <h3>SVG Rendering Test:</h3>
    <div class="svg-container">
        {svg_content}
    </div>
    
    <div class="warning">
        <strong>Note:</strong> If you can see the diagram above, SVG is working correctly. 
        If not, there might be an issue with the SVG content or browser compatibility.
    </div>
    
    <h3>SVG Source Code (First 1000 characters):</h3>
    <pre style="background: #f8f9fa; padding: 10px; border: 1px solid #ddd; overflow-x: auto;">
{svg_content[:1000]}...</pre>

</body>
</html>
"""
            
            # Write to file
            with open('svg_test_output.html', 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print("✅ Created svg_test_output.html")
            print("📂 Open this file in your browser to test SVG rendering")
            print(f"📊 SVG length: {len(svg_content)} characters")
            
            # Also check for common SVG issues
            print("\n🔍 SVG Analysis:")
            if svg_content.startswith('<?xml'):
                print("✅ SVG starts with XML declaration")
            elif svg_content.startswith('<svg'):
                print("✅ SVG starts with <svg> tag")
            else:
                print("❌ SVG doesn't start with expected tags")
                print(f"First 50 chars: {svg_content[:50]}")
            
            if 'width=' in svg_content and 'height=' in svg_content:
                print("✅ SVG has width and height attributes")
            else:
                print("⚠️ SVG might be missing width/height attributes")
            
            if 'viewBox=' in svg_content or 'viewbox=' in svg_content:
                print("✅ SVG has viewBox attribute")
            else:
                print("⚠️ SVG might be missing viewBox attribute")
            
        else:
            print("❌ No SVG content found")
            
    except Product.DoesNotExist:
        print("❌ Product not found")

if __name__ == "__main__":
    create_svg_test_file()

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from oscar.apps.catalogue.models import Product
from motorpartsdata.templatetags.parts_tags import get_product_svg

def svg_debug_view(request, product_id=None):
    """Debug view to test SVG rendering"""
    
    if not product_id:
        product_id = 2429  # The ID from the debug script
    
    try:
        product = get_object_or_404(Product, id=product_id)
        svg_content = get_product_svg(product)
        
        if svg_content:
            # Create a simple test page
            html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>SVG Debug for {product.title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .info {{ background: #d4edda; padding: 15px; margin: 15px 0; border-radius: 5px; }}
        .svg-container {{ 
            border: 2px solid #007bff; 
            padding: 20px; 
            margin: 20px 0; 
            background: white;
            min-height: 400px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .debug {{ background: #f8f9fa; padding: 10px; margin: 10px 0; border: 1px solid #ddd; font-family: monospace; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 SVG Debug for Product #{product.id}</h1>
        
        <div class="info">
            <strong>Product:</strong> {product.title}<br>
            <strong>UPC:</strong> {product.upc}<br>
            <strong>SVG Found:</strong> ✅ Yes<br>
            <strong>SVG Length:</strong> {len(svg_content)} characters<br>
        </div>
        
        <h2>SVG Rendering Test:</h2>
        <div class="svg-container">
            {svg_content}
        </div>
        
        <details>
            <summary>Show SVG Source (First 2000 characters)</summary>
            <div class="debug">
{svg_content[:2000]}...
            </div>
        </details>
        
        <p><a href="/catalogue/part-{product.slug}_{product.id}/">← Back to Product Page</a></p>
    </div>
</body>
</html>
"""
            return HttpResponse(html, content_type='text/html')
        else:
            return HttpResponse(f"<h1>❌ No SVG found for product {product.title}</h1><p>UPC: {product.upc}</p>")
            
    except Product.DoesNotExist:
        return HttpResponse(f"<h1>❌ Product with ID {product_id} not found</h1>")

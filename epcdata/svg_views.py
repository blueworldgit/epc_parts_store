from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.shortcuts import render
from oscar.apps.catalogue.models import Product
from motorpartsdata.models import Part, ChildTitle

@require_http_methods(["GET"])
def svg_diagram_view(request, upc):
    """Return SVG diagram data for a product UPC"""
    try:
        part = Part.objects.get(part_number=upc)
        child_title = part.child_title
        
        if child_title and child_title.svg_code:
            return JsonResponse({
                'success': True,
                'title': child_title.title,
                'svg_code': child_title.svg_code
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'No SVG diagram available'
            })
    except (Part.DoesNotExist, ChildTitle.DoesNotExist):
        return JsonResponse({
            'success': False,
            'message': 'Part not found'
        })

def svg_test_view(request):
    """Test view to check SVG functionality"""
    # Get a few products to test with
    test_products = Product.objects.all()[:5]
    
    context = {
        'test_products': test_products,
    }
    return render(request, 'svg_test.html', context)

def find_svg_products_view(request):
    """View to find products with SVG data"""
    return render(request, 'find_svg_products.html')

def svg_debug_api(request):
    """API endpoint to debug SVG data"""
    # Get specific product if requested
    product_slug = request.GET.get('product_slug')
    if product_slug:
        try:
            product = Product.objects.get(slug=product_slug)
            data = {
                'product_found': True,
                'product_title': product.title,
                'product_id': product.id,
                'product_upc': product.upc,
                'product_slug': product.slug,
                'has_primary_image': bool(product.primary_image),
                'primary_image_url': product.primary_image.original.url if product.primary_image and product.primary_image.original else None,
                'svg_data': None
            }
            
            # Check for SVG data
            if product.upc:
                try:
                    # Handle both direct part numbers and EPC-prefixed UPCs
                    part_number = product.upc
                    if part_number.startswith('EPC-'):
                        part_number = part_number[4:]  # Remove "EPC-" prefix
                    
                    part = Part.objects.get(part_number=part_number)
                    if part.child_title and part.child_title.svg_code:
                        data['svg_data'] = {
                            'found': True,
                            'child_title': part.child_title.title,
                            'svg_length': len(part.child_title.svg_code),
                            'svg_preview': part.child_title.svg_code[:200],
                            'part_number_used': part_number,
                            'original_upc': product.upc
                        }
                    else:
                        data['svg_data'] = {'found': False, 'reason': 'No ChildTitle or SVG code', 'part_number_used': part_number}
                except Part.DoesNotExist:
                    data['svg_data'] = {'found': False, 'reason': f'No part found with part_number: {part_number} (from UPC: {product.upc})'}
            else:
                data['svg_data'] = {'found': False, 'reason': 'Product has no UPC'}
                
            return JsonResponse(data)
        except Product.DoesNotExist:
            return JsonResponse({'product_found': False, 'error': f'Product not found: {product_slug}'})
    
    # Find products with SVG data
    find_svg = request.GET.get('find_svg', False)
    if find_svg:
        # Find ChildTitles with SVG data
        child_titles_with_svg = ChildTitle.objects.filter(
            svg_code__isnull=False
        ).exclude(svg_code='')[:10]
        
        data = {
            'search_type': 'find_svg_products',
            'child_titles_count': child_titles_with_svg.count(),
            'products_with_svg': [],
            'sample_upcs': {
                'products': [],
                'parts': []
            }
        }
        
        products_found = 0
        for ct in child_titles_with_svg:
            # Find parts linked to this ChildTitle
            parts = Part.objects.filter(child_title=ct)[:3]
            
            for part in parts:
                # Check if there's a Product with this UPC
                try:
                    product = Product.objects.get(upc=part.part_number)
                    products_found += 1
                    data['products_with_svg'].append({
                        'product_title': product.title,
                        'product_slug': product.slug,
                        'product_id': product.id,
                        'product_upc': product.upc,
                        'child_title': ct.title,
                        'svg_length': len(ct.svg_code),
                        'url': f'http://127.0.0.1:8000/catalogue/{product.slug}/',
                        'direct_url': f'http://127.0.0.1:8000/catalogue/{product.id}/'
                    })
                    break  # Found one, move to next ChildTitle
                except Product.DoesNotExist:
                    continue
        
        # Sample data for debugging
        sample_products = Product.objects.all()[:5]
        for p in sample_products:
            data['sample_upcs']['products'].append({
                'title': p.title[:50],
                'upc': p.upc
            })
        
        sample_parts = Part.objects.all()[:5]
        for p in sample_parts:
            data['sample_upcs']['parts'].append({
                'part_number': p.part_number
            })
        
        data['summary'] = {
            'child_titles_with_svg': child_titles_with_svg.count(),
            'products_with_svg_found': products_found
        }
        
        return JsonResponse(data)
    
    # Default: Check ChildTitle objects with SVG
    child_titles_with_svg = ChildTitle.objects.filter(svg_code__isnull=False).exclude(svg_code='')[:5]
    
    data = {
        'child_titles_count': child_titles_with_svg.count(),
        'samples': []
    }
    
    for ct in child_titles_with_svg:
        sample = {
            'title': ct.title,
            'svg_length': len(ct.svg_code) if ct.svg_code else 0,
            'parts': []
        }
        
        # Find parts linked to this ChildTitle
        parts = Part.objects.filter(child_title=ct)[:3]
        
        for part in parts:
            part_data = {
                'part_number': part.part_number,
                'product_exists': False,
                'product_id': None,
                'product_title': None
            }
            
            # Check if there's a Product with this UPC
            try:
                product = Product.objects.get(upc=part.part_number)
                part_data['product_exists'] = True
                part_data['product_id'] = product.id
                part_data['product_title'] = product.title
            except Product.DoesNotExist:
                pass
                
            sample['parts'].append(part_data)
        
        data['samples'].append(sample)
    
    return JsonResponse(data)
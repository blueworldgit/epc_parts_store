from oscar.core.loading import get_model
from django.conf import settings

def uren_context(request):
    """
    Context processor to provide common data for Uren template.
    """
    Category = get_model('catalogue', 'Category')
    Product = get_model('catalogue', 'Product')
    
    # Get root categories (depth=1) which should be the "Serial ..." categories
    root_categories = Category.objects.filter(depth=1).select_related()
    
    # Get featured products (first 8 products with stock)
    featured_products = Product.objects.filter(
        stockrecords__isnull=False
    ).distinct()[:8]
    
    context = {
        'categories': root_categories,
        'featured_products': featured_products,
        'settings': settings,
    }
    
    # Include basket if it exists (Oscar's middleware should have added it to request)
    if hasattr(request, 'basket'):
        context['basket'] = request.basket
    
    return context

def vehicle_brands_context(request):
    """
    Context processor to provide vehicle brands and their serial categories
    to all templates for the navigation dropdown
    """
    try:
        Category = get_model('catalogue', 'Category')
        
        # Get all vehicle brand categories (direct children of root)
        vehicle_brands = Category.objects.filter(depth=1).order_by('name')
        
        # Create a structure with brands and their serial subcategories
        vehicle_dropdown_data = []
        for brand in vehicle_brands:
            # Get serial categories for this brand
            serial_categories = brand.get_children().order_by('name')
            vehicle_dropdown_data.append({
                'brand': brand,
                'serials': serial_categories
            })
        
        return {
            'vehicle_dropdown_data': vehicle_dropdown_data
        }
    except Exception as e:
        # Return empty data if there's an error
        return {
            'vehicle_dropdown_data': []
        }

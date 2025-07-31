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

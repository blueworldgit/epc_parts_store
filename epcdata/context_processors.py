from oscar.core.loading import get_model

Category = get_model('catalogue', 'Category')

def categories_processor(request):
    """
    Context processor to add categories to all templates
    """
    try:
        # Get all root categories (those without a parent)
        categories = Category.objects.filter(depth=1).select_related().prefetch_related('children')
        return {'categories': categories}
    except:
        return {'categories': []}

def vehicle_brands_context(request):
    """
    Context processor to provide vehicle brands and their serial categories
    to all templates for the navigation dropdown
    """
    try:
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

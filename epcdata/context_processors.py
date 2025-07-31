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

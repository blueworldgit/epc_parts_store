from django import template
from oscar.apps.catalogue.models import Category

register = template.Library()

@register.inclusion_tag('oscar/partials/dynamic_category_sidebar.html', takes_context=True)
def dynamic_category_sidebar(context):
    """
    Display a dynamic hierarchical category sidebar that changes based on current page
    """
    request = context.get('request')
    current_category = context.get('category', None)
    
    # Get all root categories (depth=1) for homepage display
    root_categories = Category.objects.filter(depth=1).prefetch_related('children')
    
    return {
        'root_categories': root_categories,
        'current_category': current_category,
        'request': request,
    }

@register.simple_tag
def get_brand_categories():
    """
    Get main brand categories (Maxus, Peugeot, etc.)
    """
    brand_names = ['maxus', 'peugeot', 'iveco', 'ldv', 'leyland']
    brand_categories = []
    
    for brand_name in brand_names:
        try:
            category = Category.objects.filter(
                name__icontains=brand_name,
                depth=1
            ).first()
            if category:
                brand_categories.append(category)
        except Category.DoesNotExist:
            continue
    
    return brand_categories

@register.filter
def contains(value, arg):
    """
    Check if value contains the argument (case insensitive)
    """
    if value and arg:
        return arg.lower() in value.lower()
    return False

@register.filter
def clean_category_name(value):
    """
    Clean category names for display (remove prefixes like 'Serial:')
    """
    if not value:
        return value
    
    # Remove common prefixes
    prefixes_to_remove = ['Serial:', 'Parent:', 'Child:']
    for prefix in prefixes_to_remove:
        if value.startswith(prefix):
            return value.replace(prefix, '').strip()
    
    return value

@register.simple_tag(takes_context=True)
def get_breadcrumb_categories(context):
    """
    Get breadcrumb navigation for current category
    """
    current_category = context.get('category', None)
    breadcrumbs = []
    
    if current_category:
        category = current_category
        while category:
            breadcrumbs.insert(0, category)
            category = category.get_parent()
    
    return breadcrumbs

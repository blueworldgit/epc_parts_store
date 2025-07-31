from django import template
from oscar.apps.catalogue.models import Category

register = template.Library()

@register.inclusion_tag('oscar/partials/category_sidebar.html')
def category_sidebar():
    """
    Display a hierarchical category sidebar similar to vanparts-direct.co.uk
    """
    # Get all root categories (depth=1) and their immediate children
    root_categories = Category.objects.filter(depth=1).prefetch_related('get_children')
    
    return {
        'root_categories': root_categories,
    }

@register.simple_tag
def get_category_tree():
    """
    Get the complete category tree for navigation
    """
    return Category.get_tree()

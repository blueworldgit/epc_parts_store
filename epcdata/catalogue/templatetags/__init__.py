from django import template
from oscar.apps.catalogue.models import Product

register = template.Library()

@register.simple_tag
def count_category_products(category):
    """Count total products in category and its descendants"""
    try:
        if not category:
            return 0
        
        # Get this category and all its descendants
        categories = [category] + list(category.get_descendants())
        
        # Count products in these categories
        count = Product.objects.filter(categories__in=categories).distinct().count()
        return count
    except:
        return 0

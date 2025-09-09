from django import template
from oscar.apps.catalogue.models import Product

register = template.Library()

@register.simple_tag
def get_category_total_products(category):
    """Get total product count for category and all its descendants"""
    if not category:
        return 0
    
    try:
        # Get this category and all its descendants
        categories = [category] + list(category.get_descendants())
        
        # Count distinct products across all these categories
        total_products = Product.objects.filter(categories__in=categories).distinct().count()
        
        return total_products
    except:
        return 0

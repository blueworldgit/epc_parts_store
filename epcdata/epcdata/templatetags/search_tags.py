from django import template
from oscar.apps.catalogue.models import Product
from django.db.models import Q

register = template.Library()

@register.simple_tag
def direct_product_search(query, limit=20):
    """
    Direct database search for products when Haystack pagination is broken
    """
    if not query:
        return []
    
    # Search in title, description, and UPC
    search_query = Q(title__icontains=query) | Q(description__icontains=query) | Q(upc__icontains=query)
    
    # Also search in categories
    search_query |= Q(categories__name__icontains=query)
    
    products = Product.objects.filter(search_query).distinct()[:limit]
    
    return products

@register.simple_tag
def direct_product_search_count(query):
    """
    Get count of products matching the search query
    """
    if not query:
        return 0
    
    # Search in title, description, and UPC
    search_query = Q(title__icontains=query) | Q(description__icontains=query) | Q(upc__icontains=query)
    
    # Also search in categories
    search_query |= Q(categories__name__icontains=query)
    
    count = Product.objects.filter(search_query).distinct().count()
    
    return count

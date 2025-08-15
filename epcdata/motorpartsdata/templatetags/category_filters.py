import re
from django import template
from oscar.apps.catalogue.models import Category, Product
from django.db.models import Q

register = template.Library()

@register.filter
def clean_category_name(value):
    """
    Clean category names by removing serial codes and improving formatting.
    """
    if not value:
        return value
    
    # Remove serial codes like JE140A001, LSH14C4C5NA129710, etc.
    cleaned = re.sub(r'[A-Z]{2,}\d+[A-Z]*\d*', '', str(value))
    
    # Remove extra spaces and "Serial" prefix
    cleaned = re.sub(r'Serial\s+', '', cleaned)
    
    # Clean up extra spaces
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    # If empty after cleaning, return original
    if not cleaned:
        return value
    
    return cleaned

@register.filter
def beautify_category_name(value):
    """
    Beautify category names for better display.
    """
    if not value:
        return value
    
    # First clean the name
    cleaned = clean_category_name(value)
    
    # Map common terms to better names
    replacements = {
        'sealant & body attachment': 'Sealant & Body Parts',
        'rear lamp': 'Rear Lights',
        'front lamp': 'Front Lights',
        'engine mount': 'Engine Mounting',
        'brake pad': 'Brake Pads',
        'brake disc': 'Brake Discs',
        'suspension arm': 'Suspension Arms',
        'fuel pump': 'Fuel Pumps',
        'air filter': 'Air Filters',
        'oil filter': 'Oil Filters',
        'spark plug': 'Spark Plugs',
        'timing belt': 'Timing Belts',
        'water pump': 'Water Pumps',
        'radiator': 'Radiators',
        'exhaust': 'Exhaust System',
        'clutch': 'Clutch System',
        'transmission': 'Transmission Parts',
        'steering': 'Steering Components',
        'wheel bearing': 'Wheel Bearings',
        'cv joint': 'CV Joints',
        'shock absorber': 'Shock Absorbers',
        'strut': 'Struts',
        'spring': 'Springs',
        'bushing': 'Bushings',
        'sensor': 'Sensors',
        'switch': 'Switches',
        'relay': 'Relays',
        'fuse': 'Fuses',
        'wire': 'Wiring',
        'cable': 'Cables',
        'hose': 'Hoses',
        'gasket': 'Gaskets',
        'seal': 'Seals',
        'bearing': 'Bearings',
        'belt': 'Belts',
        'chain': 'Chains',
        'pulley': 'Pulleys',
        'tensioner': 'Tensioners',
        'alternator': 'Alternators',
        'starter': 'Starters',
        'battery': 'Batteries',
        'ignition': 'Ignition System',
        'cooling': 'Cooling System',
        'heating': 'Heating System',
        'air conditioning': 'Air Conditioning',
        'windshield': 'Windshield',
        'mirror': 'Mirrors',
        'door': 'Door Parts',
        'window': 'Window Parts',
        'seat': 'Seats',
        'dashboard': 'Dashboard',
        'console': 'Console',
        'trim': 'Interior Trim',
        'carpet': 'Carpets',
        'mat': 'Floor Mats',
        'bumper': 'Bumpers',
        'fender': 'Fenders',
        'hood': 'Hoods',
        'trunk': 'Trunk Parts',
        'roof': 'Roof Parts',
        'spoiler': 'Spoilers',
        'grille': 'Grilles',
        'molding': 'Moldings',
        'emblem': 'Emblems',
        'badge': 'Badges',
    }
    
    # Apply replacements
    cleaned_lower = cleaned.lower()
    for old, new in replacements.items():
        if old in cleaned_lower:
            cleaned = new
            break
    
    # Title case if no replacement found
    if cleaned == clean_category_name(value):
        cleaned = cleaned.title()
    
    return cleaned

@register.filter
def recursive_product_count(category):
    """
    Get the total count of products in this category and all its descendants
    """
    if not category:
        return 0
    
    # Get all descendant categories and include the current category
    descendant_categories = list(category.get_descendants()) + [category]
    
    # Count products in all these categories
    product_count = Product.objects.filter(categories__in=descendant_categories).distinct().count()
    
    return product_count

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

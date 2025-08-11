from django import template
from motorpartsdata.models import Part, ChildTitle
import re

register = template.Library()

@register.simple_tag
def get_product_svg(product):
    """Get SVG content for a product based on its UPC."""
    try:
        if product.upc:
            # Handle both direct part numbers and EPC-prefixed UPCs
            part_number = product.upc
            
            # If UPC has EPC- prefix, remove it
            if part_number.startswith('EPC-'):
                part_number = part_number[4:]  # Remove "EPC-" prefix
            
            part = Part.objects.select_related('child_title').get(part_number=part_number)
            if part.child_title and part.child_title.svg_code:
                return part.child_title.svg_code
    except Part.DoesNotExist:
        pass
    except Exception as e:
        # For debugging, you can log the error
        pass
    return None

@register.filter
def svg_diagram(product):
    """Filter to get SVG diagram for a product."""
    try:
        if product.upc:
            # Handle both direct part numbers and EPC-prefixed UPCs
            part_number = product.upc
            
            # If UPC has EPC- prefix, remove it
            if part_number.startswith('EPC-'):
                part_number = part_number[4:]  # Remove "EPC-" prefix
            
            part = Part.objects.select_related('child_title').get(part_number=part_number)
            if part.child_title and part.child_title.svg_code:
                return part.child_title.svg_code
    except Part.DoesNotExist:
        pass
    except Exception as e:
        # For debugging, you can log the error
        pass
    return None

@register.simple_tag
def debug_product_info(product):
    """Debug tag to show product-part relationship info."""
    try:
        if product.upc:
            part = Part.objects.select_related('child_title').get(part_number=product.upc)
            return f"Found part: {part.part_number}, SVG available: {bool(part.child_title and part.child_title.svg_code)}"
        else:
            return "No UPC set for product"
    except Part.DoesNotExist:
        return f"No part found for UPC: {product.upc}"
    except Exception as e:
        return f"Error: {str(e)}"

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
def remove_part_number(title):
    """Remove part number prefix from product title."""
    if not title:
        return title
    
    # Pattern to match part numbers at the start: letters/numbers followed by space/dash
    # Examples: "C00220787 - Product Name" or "EPC-C00220787 Product Name"
    pattern = r'^(EPC-)?[A-Z0-9]+([\s\-_]+)'
    
    # Remove the part number prefix
    cleaned_title = re.sub(pattern, '', title, flags=re.IGNORECASE)
    
    # If nothing left after cleaning, return original
    if not cleaned_title.strip():
        return title
        
    return cleaned_title.strip()

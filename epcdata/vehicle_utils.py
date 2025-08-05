"""
Utility functions for determining vehicle brands and managing Oscar categories
"""
import re
from django.core.exceptions import ObjectDoesNotExist
from oscar.apps.catalogue.models import Category


def determine_vehicle_brand(serial_number):
    """
    Determine vehicle brand from serial number pattern
    Add your own logic based on serial number patterns
    """
    serial = serial_number.upper()
    
    # Define patterns for different vehicle brands
    patterns = {
        'Maxus': [
            r'^LSH',  # LSH prefix typically for Maxus
            r'^LDV',  # LDV prefix for Maxus
            r'^MX',   # MX prefix for Maxus
        ],
        'Peugeot': [
            r'^WJZ',  # Common Peugeot pattern
            r'^VF3',  # Peugeot VIN pattern
            r'^PG',   # PG prefix
        ],
        'Renault': [
            r'^VF1',  # Renault VIN pattern
            r'^RN',   # RN prefix
            r'^RE',   # RE prefix
        ],
        'Mercedes': [
            r'^WDF',  # Mercedes commercial vehicle pattern
            r'^WDB',  # Mercedes pattern
            r'^MB',   # MB prefix
        ],
        'MAN': [
            r'^WMA',  # MAN VIN pattern
            r'^MN',   # MN prefix
        ]
    }
    
    # Check patterns
    for brand, brand_patterns in patterns.items():
        for pattern in brand_patterns:
            if re.match(pattern, serial):
                return brand
    
    # Default to Maxus if no pattern matches
    return 'Maxus'


def get_or_create_vehicle_category(brand_name):
    """
    Get existing vehicle category or create if doesn't exist
    """
    try:
        category = Category.objects.get(name=brand_name, depth=1)
        return category
    except ObjectDoesNotExist:
        # Create new category if it doesn't exist
        category = Category.add_root(name=brand_name, slug=brand_name.lower())
        return category


def get_or_create_serial_category(serial_number, vehicle_category):
    """
    Create serial number category under the vehicle category
    """
    serial_name = f"Serial {serial_number}"
    serial_slug = f"serial-{serial_number.lower().replace('_', '-')}"
    
    # Check if serial category already exists under this vehicle
    for child in vehicle_category.get_children():
        if child.name == serial_name:
            return child
    
    # Create new serial category under vehicle category
    serial_category = vehicle_category.add_child(
        name=serial_name,
        slug=serial_slug
    )
    return serial_category

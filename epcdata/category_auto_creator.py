"""
Enhanced data loading utilities that automatically create Oscar categories
when processing motor parts data.
"""
import logging
from oscar.apps.catalogue.models import Category
from motorpartsdata.models import SerialNumber, ParentTitle, ChildTitle

logger = logging.getLogger(__name__)

def create_oscar_category_for_serial(serial_instance):
    """Create or get Oscar category for a SerialNumber"""
    category_name = f"Serial: {serial_instance.serial}"
    
    try:
        category, created = Category.objects.get_or_create(
            name=category_name,
            defaults={
                'description': f'Parts for serial number {serial_instance.serial}',
                'slug': f'serial-{serial_instance.serial}',
            }
        )
        
        # If it's a new category and has no parent, make it a root category
        if created and not category.get_parent():
            # Move to root level if not already there
            try:
                if category.depth != 1:
                    Category.objects.filter(id=category.id).update(depth=1, numchild=0, path='0001')
                    category.refresh_from_db()
            except Exception as e:
                logger.warning(f"Could not set category as root: {e}")
        
        if created:
            logger.info(f"📁 Created Oscar category: {category_name}")
        else:
            logger.debug(f"📁 Using existing Oscar category: {category_name}")
            
        return category
        
    except Exception as e:
        logger.error(f"Error creating category for serial {serial_instance.serial}: {e}")
        return None

def create_oscar_category_for_parent(parent_instance, serial_category=None):
    """Create or get Oscar category for a ParentTitle"""
    category_name = f"Parent: {parent_instance.title}"
    
    try:
        category, created = Category.objects.get_or_create(
            name=category_name,
            defaults={
                'description': f'Parent category: {parent_instance.title}',
                'slug': f'parent-{parent_instance.id}',
            }
        )
        
        # If it's a new category and has no parent, make it a root category
        if created and not category.get_parent():
            try:
                if category.depth != 1:
                    Category.objects.filter(id=category.id).update(depth=1, numchild=0, path=f'{category.id:04d}')
                    category.refresh_from_db()
            except Exception as e:
                logger.warning(f"Could not set category as root: {e}")
        
        if created:
            logger.info(f"📂 Created Oscar category: {category_name}")
        else:
            logger.debug(f"📂 Using existing Oscar category: {category_name}")
            
        return category
        
    except Exception as e:
        logger.error(f"Error creating category for parent {parent_instance.title}: {e}")
        return None

def create_oscar_category_for_child(child_instance, parent_category=None):
    """Create or get Oscar category for a ChildTitle"""
    category_name = f"Child: {child_instance.title}"
    
    try:
        category, created = Category.objects.get_or_create(
            name=category_name,
            defaults={
                'description': f'Child category: {child_instance.title}',
                'slug': f'child-{child_instance.id}',
            }
        )
        
        # If it's a new category and has no parent, make it a root category
        if created and not category.get_parent():
            try:
                if category.depth != 1:
                    Category.objects.filter(id=category.id).update(depth=1, numchild=0, path=f'{category.id:04d}')
                    category.refresh_from_db()
            except Exception as e:
                logger.warning(f"Could not set category as root: {e}")
        
        if created:
            logger.info(f"📄 Created Oscar category: {category_name}")
        else:
            logger.debug(f"📄 Using existing Oscar category: {category_name}")
            
        return category
        
    except Exception as e:
        logger.error(f"Error creating category for child {child_instance.title}: {e}")
        return None

def auto_create_categories_for_data(serial_instance=None, parent_instance=None, child_instance=None):
    """
    Automatically create Oscar categories for new data.
    Call this function whenever you create new SerialNumber, ParentTitle, or ChildTitle instances.
    """
    created_categories = []
    
    try:
        # Create category for serial if provided
        if serial_instance:
            serial_cat = create_oscar_category_for_serial(serial_instance)
            if serial_cat:
                created_categories.append(serial_cat)
        
        # Create category for parent if provided
        if parent_instance:
            # Get the serial category if it exists
            serial_cat = None
            if hasattr(parent_instance, 'serial_number'):
                serial_cat = create_oscar_category_for_serial(parent_instance.serial_number)
                if serial_cat and serial_cat not in created_categories:
                    created_categories.append(serial_cat)
            
            parent_cat = create_oscar_category_for_parent(parent_instance, serial_cat)
            if parent_cat:
                created_categories.append(parent_cat)
        
        # Create category for child if provided
        if child_instance:
            # Get the parent and serial categories if they exist
            parent_cat = None
            serial_cat = None
            
            if hasattr(child_instance, 'parent'):
                parent_cat = create_oscar_category_for_parent(child_instance.parent)
                if parent_cat and parent_cat not in created_categories:
                    created_categories.append(parent_cat)
                
                if hasattr(child_instance.parent, 'serial_number'):
                    serial_cat = create_oscar_category_for_serial(child_instance.parent.serial_number)
                    if serial_cat and serial_cat not in created_categories:
                        created_categories.append(serial_cat)
            
            child_cat = create_oscar_category_for_child(child_instance, parent_cat)
            if child_cat:
                created_categories.append(child_cat)
        
        return created_categories
        
    except Exception as e:
        logger.error(f"Error in auto_create_categories_for_data: {e}")
        return created_categories

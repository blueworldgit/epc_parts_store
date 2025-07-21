#!/usr/bin/env python
"""
Script to link existing Oscar products to categories based on your motor parts data.
This helps organize your 1,601 existing products into the new category structure.
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from oscar.apps.catalogue.models import Category, Product, ProductCategory
from motorpartsdata.models import Part, ChildTitle, ParentTitle, SerialNumber
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def link_products_to_categories():
    """Link Oscar products to categories based on motor parts data relationships"""
    
    logger.info("🔗 Starting product-category linking process")
    
    linked_count = 0
    not_found_count = 0
    
    # Get all Oscar products
    products = Product.objects.all()
    logger.info(f"Found {products.count()} Oscar products to process")
    
    for product in products:
        try:
            # Try to find a matching Part by UPC/part_number
            part = None
            
            # First try matching by UPC
            if product.upc:
                part = Part.objects.filter(part_number=product.upc).first()
            
            # If not found by UPC, try by title/name
            if not part and product.title:
                part = Part.objects.filter(usage_name__icontains=product.title[:50]).first()
            
            if part:
                # Find the appropriate categories for this part
                child_title = part.child_title
                parent_title = child_title.parent
                serial_number = parent_title.serial_number
                
                # Find corresponding Oscar categories
                categories_to_link = []
                
                # Serial category
                serial_cat = Category.objects.filter(name=f"Serial: {serial_number.serial}").first()
                if serial_cat:
                    categories_to_link.append(serial_cat)
                
                # Parent category
                parent_cat = Category.objects.filter(name=f"Parent: {parent_title.title}").first()
                if parent_cat:
                    categories_to_link.append(parent_cat)
                
                # Child category
                child_cat = Category.objects.filter(name=f"Child: {child_title.title}").first()
                if child_cat:
                    categories_to_link.append(child_cat)
                
                # Link the product to categories
                for category in categories_to_link:
                    product_category, created = ProductCategory.objects.get_or_create(
                        product=product,
                        category=category
                    )
                    if created:
                        logger.info(f"✅ Linked product '{product.title}' to category '{category.name}'")
                        linked_count += 1
                
            else:
                logger.debug(f"❌ No matching part found for product: {product.title} (UPC: {product.upc})")
                not_found_count += 1
                
        except Exception as e:
            logger.error(f"Error processing product {product.id}: {e}")
    
    logger.info(f"🎯 Linking complete:")
    logger.info(f"   Linked: {linked_count} product-category relationships")
    logger.info(f"   Not found: {not_found_count} products without matching parts")

def create_category_structure_report():
    """Create a report showing the category structure"""
    
    logger.info("\n📊 Category Structure Report:")
    logger.info("=" * 50)
    
    # Count categories by type
    serial_cats = Category.objects.filter(name__startswith="Serial:").count()
    parent_cats = Category.objects.filter(name__startswith="Parent:").count()
    child_cats = Category.objects.filter(name__startswith="Child:").count()
    total_cats = Category.objects.count()
    
    logger.info(f"Serial Categories: {serial_cats}")
    logger.info(f"Parent Categories: {parent_cats}")
    logger.info(f"Child Categories: {child_cats}")
    logger.info(f"Total Categories: {total_cats}")
    
    # Count products with categories
    products_with_cats = Product.objects.filter(categories__isnull=False).distinct().count()
    total_products = Product.objects.count()
    
    logger.info(f"\nProducts with Categories: {products_with_cats}")
    logger.info(f"Total Products: {total_products}")
    logger.info(f"Uncategorized Products: {total_products - products_with_cats}")

if __name__ == "__main__":
    create_category_structure_report()
    link_products_to_categories()
    create_category_structure_report()

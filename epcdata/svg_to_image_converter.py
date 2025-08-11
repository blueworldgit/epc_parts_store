#!/usr/bin/env python
"""
Enhanced SVG to Image converter for Oscar products
Converts stored SVG data to PNG images and creates proper image fields
"""
import os
import sys
import django
from io import BytesIO
import base64
from PIL import Image
import cairosvg
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from motorpartsdata.models import ChildTitle, Part
from oscar.apps.catalogue.models import Product, ProductImage
import logging

logger = logging.getLogger(__name__)

class SVGToImageConverter:
    """Convert SVG data to images and attach to Oscar products"""
    
    def __init__(self, image_width=800, image_height=600, thumbnail_size=(300, 300)):
        self.image_width = image_width
        self.image_height = image_height
        self.thumbnail_size = thumbnail_size
    
    def convert_svg_to_png(self, svg_content):
        """Convert SVG string to PNG bytes"""
        try:
            # Clean up the SVG content if needed
            if not svg_content.strip().startswith('<svg'):
                return None
            
            # Convert SVG to PNG using cairosvg
            png_data = cairosvg.svg2png(
                bytestring=svg_content.encode('utf-8'),
                output_width=self.image_width,
                output_height=self.image_height
            )
            
            return png_data
            
        except Exception as e:
            logger.error(f"Error converting SVG to PNG: {str(e)}")
            return None
    
    def create_thumbnail(self, png_data):
        """Create thumbnail from PNG data"""
        try:
            # Open image with PIL
            image = Image.open(BytesIO(png_data))
            
            # Convert to RGB if necessary (for PNG with transparency)
            if image.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'RGBA':
                    background.paste(image, mask=image.split()[-1])
                else:
                    background.paste(image, mask=image.split()[-1])
                image = background
            
            # Create thumbnail
            image.thumbnail(self.thumbnail_size, Image.Resampling.LANCZOS)
            
            # Save to bytes
            thumbnail_buffer = BytesIO()
            image.save(thumbnail_buffer, format='PNG', optimize=True)
            
            return thumbnail_buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Error creating thumbnail: {str(e)}")
            return None
    
    def add_image_to_product(self, product, png_data, filename_base):
        """Add image to Oscar product"""
        try:
            # Create main image file
            image_file = ContentFile(png_data, name=f"{filename_base}.png")
            
            # Create thumbnail
            thumbnail_data = self.create_thumbnail(png_data)
            if thumbnail_data:
                thumbnail_file = ContentFile(thumbnail_data, name=f"{filename_base}_thumb.png")
            else:
                thumbnail_file = image_file
            
            # Create ProductImage instance
            product_image = ProductImage.objects.create(
                product=product,
                original=image_file,
                caption=f"Diagram for {product.title}",
                display_order=0
            )
            
            logger.info(f"Added image to product: {product.title}")
            return product_image
            
        except Exception as e:
            logger.error(f"Error adding image to product {product.title}: {str(e)}")
            return None
    
    def process_product(self, product):
        """Process a single product to convert its SVG to image"""
        try:
            # Get the SVG diagram attribute
            svg_attribute = product.attribute_values.filter(
                attribute__code='svg_diagram'
            ).first()
            
            if not svg_attribute or not svg_attribute.value:
                logger.info(f"No SVG diagram found for product: {product.title}")
                return False
            
            # Check if product already has images
            if product.images.exists():
                logger.info(f"Product {product.title} already has images, skipping")
                return False
            
            # Convert SVG to PNG
            png_data = self.convert_svg_to_png(svg_attribute.value)
            if not png_data:
                logger.error(f"Failed to convert SVG for product: {product.title}")
                return False
            
            # Create filename base from product
            filename_base = f"product_{product.id}_{product.upc}"
            
            # Add image to product
            product_image = self.add_image_to_product(product, png_data, filename_base)
            
            return product_image is not None
            
        except Exception as e:
            logger.error(f"Error processing product {product.title}: {str(e)}")
            return False
    
    def process_all_products(self):
        """Process all products with SVG diagrams"""
        products_with_svg = Product.objects.filter(
            attribute_values__attribute__code='svg_diagram',
            attribute_values__value__isnull=False
        ).exclude(attribute_values__value='')
        
        logger.info(f"Found {products_with_svg.count()} products with SVG diagrams")
        
        success_count = 0
        for product in products_with_svg:
            if self.process_product(product):
                success_count += 1
        
        logger.info(f"Successfully processed {success_count}/{products_with_svg.count()} products")
        return success_count

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Convert SVG diagrams to product images')
    parser.add_argument('--product-id', type=int, help='Process specific product ID only')
    parser.add_argument('--width', type=int, default=800, help='Image width (default: 800)')
    parser.add_argument('--height', type=int, default=600, help='Image height (default: 600)')
    
    args = parser.parse_args()
    
    converter = SVGToImageConverter(
        image_width=args.width,
        image_height=args.height
    )
    
    if args.product_id:
        try:
            product = Product.objects.get(id=args.product_id)
            success = converter.process_product(product)
            logger.info(f"Product {product.title}: {'Success' if success else 'Failed'}")
        except Product.DoesNotExist:
            logger.error(f"Product with ID {args.product_id} not found")
    else:
        converter.process_all_products()

if __name__ == "__main__":
    main()

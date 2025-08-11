from django.core.management.base import BaseCommand
from oscar.apps.catalogue.models import Product
from motorpartsdata.models import Part, ChildTitle

class Command(BaseCommand):
    help = 'Debug specific product SVG data'

    def add_arguments(self, parser):
        parser.add_argument('product_slug', type=str, help='Product slug to debug')

    def handle(self, *args, **options):
        product_slug = options['product_slug']
        self.stdout.write(f"=== Debugging Product: {product_slug} ===")
        
        try:
            # Find the product
            product = Product.objects.get(slug=product_slug)
            self.stdout.write(f"✅ Product found: {product.title}")
            self.stdout.write(f"   ID: {product.id}")
            self.stdout.write(f"   UPC: {product.upc}")
            self.stdout.write(f"   Slug: {product.slug}")
            
            # Check for primary image
            if product.primary_image:
                self.stdout.write(f"   Primary Image: {product.primary_image}")
                if product.primary_image.original:
                    self.stdout.write(f"   Image URL: {product.primary_image.original.url}")
            else:
                self.stdout.write("   ❌ No primary image")
            
            # Check for SVG data using the UPC
            if product.upc:
                self.stdout.write(f"\n🔍 Checking SVG data for UPC: {product.upc}")
                try:
                    part = Part.objects.get(part_number=product.upc)
                    self.stdout.write(f"   ✅ Part found: {part.part_number}")
                    
                    if part.child_title:
                        self.stdout.write(f"   ✅ ChildTitle found: {part.child_title.title}")
                        
                        if part.child_title.svg_code:
                            svg_length = len(part.child_title.svg_code)
                            self.stdout.write(f"   ✅ SVG data found: {svg_length} characters")
                            
                            # Show first 200 characters of SVG
                            svg_preview = part.child_title.svg_code[:200]
                            self.stdout.write(f"   SVG Preview: {svg_preview}...")
                        else:
                            self.stdout.write(f"   ❌ No SVG data in ChildTitle")
                    else:
                        self.stdout.write(f"   ❌ No ChildTitle linked to part")
                        
                except Part.DoesNotExist:
                    self.stdout.write(f"   ❌ No part found with UPC: {product.upc}")
            else:
                self.stdout.write("   ❌ Product has no UPC")
                
        except Product.DoesNotExist:
            self.stdout.write(f"❌ Product not found with slug: {product_slug}")

from django.core.management.base import BaseCommand
from motorpartsdata.models import Part, ChildTitle
from catalogue.models import Product

class Command(BaseCommand):
    help = 'Test SVG data availability'

    def handle(self, *args, **options):
        self.stdout.write("=== Testing SVG Data ===")
        
        # Check ChildTitle objects with SVG
        child_titles_with_svg = ChildTitle.objects.filter(svg_code__isnull=False).exclude(svg_code='')[:5]
        self.stdout.write(f"\nChildTitles with SVG: {child_titles_with_svg.count()}")
        
        for ct in child_titles_with_svg:
            self.stdout.write(f"ChildTitle: {ct.title} - SVG length: {len(ct.svg_code) if ct.svg_code else 0}")
            
            # Find parts linked to this ChildTitle
            parts = Part.objects.filter(child_title=ct)[:3]
            self.stdout.write(f"  Linked parts: {parts.count()}")
            
            for part in parts:
                self.stdout.write(f"    Part: {part.part_number}")
                
                # Check if there's a Product with this UPC
                try:
                    product = Product.objects.get(upc=part.part_number)
                    self.stdout.write(f"      Product found: {product.title} (ID: {product.id})")
                    self.stdout.write(f"      URL: http://127.0.0.1:8000/catalogue/{product.id}/")
                except Product.DoesNotExist:
                    self.stdout.write(f"      No product found with UPC: {part.part_number}")
            self.stdout.write("")

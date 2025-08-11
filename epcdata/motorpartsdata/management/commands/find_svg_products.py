from django.core.management.base import BaseCommand
from oscar.apps.catalogue.models import Product
from motorpartsdata.models import Part, ChildTitle

class Command(BaseCommand):
    help = 'Find products with SVG data'

    def handle(self, *args, **options):
        self.stdout.write("=== Finding Products with SVG Data ===")
        
        # Find ChildTitles with SVG data
        child_titles_with_svg = ChildTitle.objects.filter(
            svg_code__isnull=False
        ).exclude(svg_code='')[:10]
        
        self.stdout.write(f"\nFound {child_titles_with_svg.count()} ChildTitles with SVG data")
        
        products_found = 0
        for ct in child_titles_with_svg:
            self.stdout.write(f"\nChildTitle: {ct.title}")
            self.stdout.write(f"SVG Length: {len(ct.svg_code)} characters")
            
            # Find parts linked to this ChildTitle
            parts = Part.objects.filter(child_title=ct)[:5]
            self.stdout.write(f"Linked parts: {parts.count()}")
            
            for part in parts:
                # Check if there's a Product with this UPC
                try:
                    product = Product.objects.get(upc=part.part_number)
                    products_found += 1
                    self.stdout.write(f"  ✅ PRODUCT FOUND!")
                    self.stdout.write(f"     Title: {product.title}")
                    self.stdout.write(f"     UPC: {product.upc}")
                    self.stdout.write(f"     Slug: {product.slug}")
                    self.stdout.write(f"     URL: http://127.0.0.1:8000/catalogue/{product.slug}/")
                    self.stdout.write(f"     Direct URL: http://127.0.0.1:8000/catalogue/{product.id}/")
                    break  # Found one, move to next ChildTitle
                except Product.DoesNotExist:
                    continue
        
        self.stdout.write(f"\n=== SUMMARY ===")
        self.stdout.write(f"ChildTitles with SVG: {child_titles_with_svg.count()}")
        self.stdout.write(f"Products with SVG found: {products_found}")
        
        if products_found == 0:
            self.stdout.write("\n⚠️  No products found with SVG data!")
            self.stdout.write("This means either:")
            self.stdout.write("1. Products and Parts have different UPC formats")
            self.stdout.write("2. SVG data exists but isn't linked to products")
            self.stdout.write("3. Products haven't been imported with matching UPCs")
            
            # Let's check some sample data
            self.stdout.write("\n=== SAMPLE DATA ANALYSIS ===")
            
            sample_products = Product.objects.all()[:5]
            self.stdout.write(f"Sample Product UPCs:")
            for p in sample_products:
                self.stdout.write(f"  Product: {p.title[:50]} - UPC: '{p.upc}'")
            
            sample_parts = Part.objects.all()[:5]
            self.stdout.write(f"\nSample Part Numbers:")
            for p in sample_parts:
                self.stdout.write(f"  Part: {p.part_number}")

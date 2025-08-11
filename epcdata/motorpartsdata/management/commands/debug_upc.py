from django.core.management.base import BaseCommand
from oscar.apps.catalogue.models import Product
from motorpartsdata.models import Part, ChildTitle

class Command(BaseCommand):
    help = 'Debug specific product SVG issues'

    def add_arguments(self, parser):
        parser.add_argument('--upc', type=str, help='Product UPC to debug', default='C00077194')

    def handle(self, *args, **options):
        upc = options['upc']
        self.stdout.write(f"=== Debugging UPC: {upc} ===")
        
        # Find products with this UPC (with or without EPC- prefix)
        products = Product.objects.filter(upc__icontains=upc)
        self.stdout.write(f"Found {products.count()} products containing '{upc}':")
        
        for product in products:
            self.stdout.write(f"\nProduct: {product.title}")
            self.stdout.write(f"  UPC: '{product.upc}'")
            
            # Test the template tag logic manually
            part_number = product.upc
            if part_number and part_number.startswith('EPC-'):
                part_number = part_number[4:]
            
            self.stdout.write(f"  Looking for part_number: '{part_number}'")
            
            try:
                part = Part.objects.select_related('child_title').get(part_number=part_number)
                self.stdout.write(f"  ✅ Part found: {part.part_number}")
                
                if part.child_title:
                    self.stdout.write(f"  ✅ ChildTitle: {part.child_title.title}")
                    
                    if part.child_title.svg_code:
                        svg_length = len(part.child_title.svg_code)
                        self.stdout.write(f"  ✅ SVG found: {svg_length} characters")
                        
                        # Check if SVG contains actual content
                        if '<svg' in part.child_title.svg_code.lower():
                            self.stdout.write(f"  ✅ Valid SVG content detected")
                        else:
                            self.stdout.write(f"  ⚠️  SVG content may be invalid")
                    else:
                        self.stdout.write(f"  ❌ No SVG code in ChildTitle")
                else:
                    self.stdout.write(f"  ❌ No ChildTitle linked to part")
                    
            except Part.DoesNotExist:
                self.stdout.write(f"  ❌ No part found with part_number: '{part_number}'")
                
                # Try to find similar part numbers
                similar_parts = Part.objects.filter(part_number__icontains=upc)
                if similar_parts.exists():
                    self.stdout.write(f"  🔍 Similar parts found:")
                    for similar in similar_parts[:5]:
                        self.stdout.write(f"    - {similar.part_number}")
            
            except Exception as e:
                self.stdout.write(f"  ❌ Error: {str(e)}")
        
        if not products.exists():
            self.stdout.write(f"❌ No products found containing UPC '{upc}'")
            
            # Show some sample products
            sample_products = Product.objects.all()[:5]
            self.stdout.write(f"\nSample products in database:")
            for p in sample_products:
                self.stdout.write(f"  - {p.title} (UPC: {p.upc})")

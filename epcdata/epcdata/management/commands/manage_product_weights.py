from django.core.management.base import BaseCommand
from oscar.apps.catalogue.models import ProductAttribute, ProductAttributeValue, Product
import csv
import os


class Command(BaseCommand):
    help = 'Manage product weights - set, update, or import from CSV'

    def add_arguments(self, parser):
        parser.add_argument(
            '--product-upc',
            type=str,
            help='UPC of the product to update weight for',
        )
        parser.add_argument(
            '--weight',
            type=float,
            help='Weight value to set (in kg)',
        )
        parser.add_argument(
            '--csv-file',
            type=str,
            help='Path to CSV file with UPC and weight columns',
        )
        parser.add_argument(
            '--export-csv',
            type=str,
            help='Export current weights to CSV file',
        )
        parser.add_argument(
            '--list-weights',
            action='store_true',
            help='List all products with their weights',
        )

    def handle(self, *args, **options):
        # Get or create weight attribute
        weight_attribute, created = ProductAttribute.objects.get_or_create(
            code='weight',
            defaults={
                'name': 'Weight',
                'type': ProductAttribute.FLOAT,
                'required': False,
                'option_group': None,
            }
        )

        if options['list_weights']:
            self.list_all_weights(weight_attribute)
        elif options['export_csv']:
            self.export_weights_to_csv(weight_attribute, options['export_csv'])
        elif options['csv_file']:
            self.import_weights_from_csv(weight_attribute, options['csv_file'])
        elif options['product_upc'] and options['weight'] is not None:
            self.set_product_weight(weight_attribute, options['product_upc'], options['weight'])
        else:
            self.stdout.write(self.style.ERROR('Please provide valid arguments. Use --help for options.'))

    def set_product_weight(self, weight_attribute, upc, weight):
        """Set weight for a specific product by UPC"""
        try:
            product = Product.objects.get(upc=upc)
            
            # Update or create weight attribute value
            weight_value, created = ProductAttributeValue.objects.update_or_create(
                attribute=weight_attribute,
                product=product,
                defaults={'value_float': weight}
            )
            
            action = "Created" if created else "Updated"
            self.stdout.write(
                self.style.SUCCESS(f'{action} weight for product {product.title} (UPC: {upc}): {weight} kg')
            )
        except Product.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Product with UPC {upc} not found.')
            )

    def import_weights_from_csv(self, weight_attribute, csv_file_path):
        """Import weights from CSV file with columns: upc, weight"""
        if not os.path.exists(csv_file_path):
            self.stdout.write(self.style.ERROR(f'CSV file not found: {csv_file_path}'))
            return

        updated_count = 0
        error_count = 0
        
        with open(csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                upc = row.get('upc', '').strip()
                weight_str = row.get('weight', '').strip()
                
                if not upc or not weight_str:
                    self.stdout.write(self.style.WARNING(f'Skipping row with missing data: {row}'))
                    continue
                
                try:
                    weight = float(weight_str)
                    product = Product.objects.get(upc=upc)
                    
                    ProductAttributeValue.objects.update_or_create(
                        attribute=weight_attribute,
                        product=product,
                        defaults={'value_float': weight}
                    )
                    
                    updated_count += 1
                    
                except (ValueError, Product.DoesNotExist) as e:
                    error_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'Error processing UPC {upc}: {str(e)}')
                    )
        
        self.stdout.write(
            self.style.SUCCESS(f'Updated {updated_count} products. {error_count} errors.')
        )

    def export_weights_to_csv(self, weight_attribute, csv_file_path):
        """Export all product weights to CSV"""
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['upc', 'title', 'weight']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            count = 0
            for product in Product.objects.all():
                weight_value = ProductAttributeValue.objects.filter(
                    attribute=weight_attribute,
                    product=product
                ).first()
                
                writer.writerow({
                    'upc': product.upc or '',
                    'title': product.title,
                    'weight': weight_value.value_float if weight_value else ''
                })
                count += 1
            
        self.stdout.write(
            self.style.SUCCESS(f'Exported {count} products to {csv_file_path}')
        )

    def list_all_weights(self, weight_attribute):
        """List all products with their weights"""
        self.stdout.write('Products with weights:')
        self.stdout.write('-' * 80)
        
        for product in Product.objects.all()[:20]:  # Limit to first 20 for display
            weight_value = ProductAttributeValue.objects.filter(
                attribute=weight_attribute,
                product=product
            ).first()
            
            weight_display = f"{weight_value.value_float} kg" if weight_value else "No weight set"
            self.stdout.write(f'{product.upc}: {product.title[:50]} - {weight_display}')
        
        total_products = Product.objects.count()
        products_with_weight = ProductAttributeValue.objects.filter(
            attribute=weight_attribute
        ).count()
        
        self.stdout.write('-' * 80)
        self.stdout.write(f'Total products: {total_products}')
        self.stdout.write(f'Products with weight: {products_with_weight}')
        self.stdout.write(f'Products without weight: {total_products - products_with_weight}')

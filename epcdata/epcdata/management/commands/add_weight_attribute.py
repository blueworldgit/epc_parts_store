from django.core.management.base import BaseCommand
from oscar.apps.catalogue.models import ProductAttribute, ProductAttributeValue, Product
from oscar.apps.catalogue.categories import create_from_breadcrumbs


class Command(BaseCommand):
    help = 'Add weight attribute to products'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-only',
            action='store_true',
            help='Only create the weight attribute, do not assign values to products',
        )

    def handle(self, *args, **options):
        # Create or get the weight attribute
        weight_attribute, created = ProductAttribute.objects.get_or_create(
            code='weight',
            defaults={
                'name': 'Weight',
                'type': ProductAttribute.FLOAT,
                'required': False,
                'option_group': None,
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created weight attribute: {weight_attribute}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Weight attribute already exists: {weight_attribute}')
            )
        
        if options['create_only']:
            self.stdout.write('Only creating attribute, skipping product assignment.')
            return
        
        # Add weight to existing products (you can customize this logic)
        products_updated = 0
        for product in Product.objects.all():
            # Check if product already has weight attribute
            existing_weight = ProductAttributeValue.objects.filter(
                attribute=weight_attribute,
                product=product
            ).first()
            
            if not existing_weight:
                # Set a default weight (you can customize this logic based on your needs)
                default_weight = self.get_default_weight_for_product(product)
                
                ProductAttributeValue.objects.create(
                    attribute=weight_attribute,
                    product=product,
                    value_float=default_weight
                )
                products_updated += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully added weight to {products_updated} products')
        )

    def get_default_weight_for_product(self, product):
        """
        Determine default weight for a product.
        You can customize this logic based on your business rules.
        """
        # Example logic - you can modify this based on your needs
        if product.product_class and product.product_class.name:
            class_name = product.product_class.name.lower()
            
            # Set different default weights based on product class
            if 'engine' in class_name:
                return 50.0  # kg
            elif 'tire' in class_name or 'wheel' in class_name:
                return 15.0  # kg
            elif 'battery' in class_name:
                return 20.0  # kg
            elif 'oil' in class_name or 'fluid' in class_name:
                return 5.0   # kg
            elif 'filter' in class_name:
                return 2.0   # kg
            elif 'brake' in class_name:
                return 8.0   # kg
            else:
                return 3.0   # kg - default for smaller parts
        
        return 3.0  # Default weight in kg

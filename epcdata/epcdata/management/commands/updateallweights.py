from django.core.management.base import BaseCommand
from oscar.apps.catalogue.models import Product, ProductAttribute, ProductAttributeValue
from oscar.apps.partner.models import StockRecord, Partner
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Update all product weights (price x 0.1) and stock numbers'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        # Get or create the weight attribute
        weight_attr, created = ProductAttribute.objects.get_or_create(
            code='weight',
            defaults={
                'name': 'Weight (kg)',
                'type': ProductAttribute.FLOAT,
                'required': False,
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Created weight attribute: {weight_attr.name}')
            )
        
        updated_products = 0
        updated_stock = 0
        zero_stock_products = 0
        
        # Process all products
        products = Product.objects.all()
        total_products = products.count()
        
        self.stdout.write(f'Processing {total_products} products...')
        
        for i, product in enumerate(products, 1):
            if i % 100 == 0:
                self.stdout.write(f'Processed {i}/{total_products} products...')
            
            try:
                # Get the product's price from stock record
                stock_record = product.stockrecords.first()
                
                if stock_record and stock_record.price and stock_record.price > 0:
                    # Calculate weight as price x 0.1
                    weight = float(stock_record.price) * 0.1
                    
                    if not dry_run:
                        # Update or create weight attribute value
                        weight_value, created = ProductAttributeValue.objects.get_or_create(
                            product=product,
                            attribute=weight_attr,
                            defaults={'value_float': weight}
                        )
                        
                        if not created and weight_value.value_float != weight:
                            weight_value.value_float = weight
                            weight_value.save()
                        
                        # Set stock to 50 for products with valid pricing
                        if stock_record.num_in_stock != 50:
                            stock_record.num_in_stock = 50
                            stock_record.save()
                            updated_stock += 1
                    
                    updated_products += 1
                    
                else:
                    # No pricing or zero pricing - set stock to 0
                    if stock_record and not dry_run:
                        if stock_record.num_in_stock != 0:
                            stock_record.num_in_stock = 0
                            stock_record.save()
                            zero_stock_products += 1
                    elif not stock_record:
                        # Create stock record with 0 stock if none exists
                        if not dry_run:
                            partner, _ = Partner.objects.get_or_create(
                                name='Default Partner',
                                defaults={'code': 'default'}
                            )
                            StockRecord.objects.create(
                                product=product,
                                partner=partner,
                                partner_sku=product.upc or f'SKU-{product.id}',
                                price=Decimal('0.00'),
                                num_in_stock=0
                            )
                            zero_stock_products += 1
                        
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error processing product {product.id}: {str(e)}')
                )
                continue
        
        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('SUMMARY:'))
        self.stdout.write(f'Total products processed: {total_products}')
        self.stdout.write(f'Products with weight updated: {updated_products}')
        self.stdout.write(f'Products with stock set to 50: {updated_stock}')
        self.stdout.write(f'Products with stock set to 0: {zero_stock_products}')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\nThis was a DRY RUN - no actual changes were made'))
            self.stdout.write('Run without --dry-run to apply these changes')
        else:
            self.stdout.write(self.style.SUCCESS('\nAll updates completed successfully!'))

        self.stdout.write(
            self.style.SUCCESS(f'Processing {total_products} products...')
        )

        for product in products:
            try:
                # Get the first stock record for this product
                stock_record = product.stockrecords.first()
                
                if stock_record:
                    price = stock_record.price
                    
                    # Calculate weight (price x 0.1)
                    if price and price > 0:
                        weight = float(price) * 0.1
                        new_stock = 50
                        stock_message = "Set to 50 (has pricing)"
                    else:
                        weight = 0.0
                        new_stock = 0
                        stock_message = "Set to 0 (no pricing or zero price)"
                        zero_stock_products += 1
                    
                    # Update or create weight attribute value
                    weight_attr_value, weight_created = ProductAttributeValue.objects.get_or_create(
                        product=product,
                        attribute=weight_attr,
                        defaults={'value_float': weight}
                    )
                    
                    if not weight_created:
                        if not dry_run:
                            weight_attr_value.value_float = weight
                            weight_attr_value.save()
                    
                    # Update stock
                    old_stock = stock_record.num_in_stock
                    if not dry_run:
                        stock_record.num_in_stock = new_stock
                        stock_record.save()
                        updated_stock_records += 1
                    
                    self.stdout.write(
                        f'Product: {product.title[:50]}... | '
                        f'Price: £{price or "0.00"} | '
                        f'Weight: {weight}kg | '
                        f'Stock: {old_stock} → {new_stock} ({stock_message})'
                    )
                    
                    updated_products += 1
                    
                else:
                    # Product has no stock record
                    self.stdout.write(
                        self.style.WARNING(
                            f'No stock record for product: {product.title[:50]}...'
                        )
                    )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'Error processing product {product.id}: {str(e)}'
                    )
                )
                logger.error(f'Error processing product {product.id}: {str(e)}')

        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('SUMMARY:'))
        self.stdout.write(f'Total products processed: {total_products}')
        self.stdout.write(f'Products with weight updated: {updated_products}')
        self.stdout.write(f'Products with stock set to 50: {updated_stock}')
        self.stdout.write(f'Products with stock set to 0: {zero_stock_products}')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\nThis was a DRY RUN - no actual changes were made'))
            self.stdout.write('Run without --dry-run to apply these changes')
        else:
            self.stdout.write(self.style.SUCCESS('\nAll updates completed successfully!'))

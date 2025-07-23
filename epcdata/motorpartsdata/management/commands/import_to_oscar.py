"""
Django management command to import motorpartsdata to Oscar
Usage: python manage.py import_to_oscar [options]
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from decimal import Decimal, InvalidOperation
import logging

from motorpartsdata.models import SerialNumber, ParentTitle, ChildTitle, Part, PricingData
from oscar.apps.catalogue.models import Product, ProductClass, Category
from oscar.apps.partner.models import Partner, StockRecord
from oscar.core.loading import get_model

# Get Oscar models
ProductAttribute = get_model('catalogue', 'ProductAttribute')
ProductAttributeValue = get_model('catalogue', 'ProductAttributeValue')


class Command(BaseCommand):
    help = 'Import motorpartsdata models to Oscar e-commerce structure'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--serial',
            type=str,
            help='Import specific serial number only',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be imported without making changes',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Verbose output',
        )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stats = {
            'categories_created': 0,
            'categories_existing': 0,
            'products_created': 0,
            'products_existing': 0,
            'stock_records_created': 0,
            'stock_records_existing': 0,
            'errors': 0
        }
    
    def handle(self, *args, **options):
        self.verbosity = options['verbosity']
        self.dry_run = options['dry_run']
        
        if self.dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No changes will be made')
            )
        
        # Setup
        self.partner = self._get_or_create_partner()
        self.product_class = self._get_or_create_product_class()
        self._setup_product_attributes()
        
        try:
            if options['serial']:
                # Import specific serial
                try:
                    serial = SerialNumber.objects.get(serial=options['serial'])
                    success = self._import_serial(serial)
                    self._print_stats()
                    if not success:
                        raise CommandError('Import failed')
                except SerialNumber.DoesNotExist:
                    raise CommandError(f"Serial number '{options['serial']}' not found")
            else:
                # Import all serials
                success = self._import_all()
                if not success:
                    raise CommandError('Import failed')
                    
        except KeyboardInterrupt:
            raise CommandError('Import interrupted by user')
    
    def _get_or_create_partner(self):
        """Get or create default partner for stock records"""
        partner, created = Partner.objects.get_or_create(
            name='EPC Motor Parts Store',
            defaults={
                'code': 'epc-store',
            }
        )
        if created:
            self.stdout.write("Created default partner: EPC Motor Parts Store")
        return partner
    
    def _get_or_create_product_class(self):
        """Get or create product class for motor parts"""
        product_class, created = ProductClass.objects.get_or_create(
            name='Motor Parts',
            defaults={
                'slug': 'motor-parts',
                'requires_shipping': True,
                'track_stock': True,
            }
        )
        if created:
            self.stdout.write("Created product class: Motor Parts")
        return product_class
    
    def _setup_product_attributes(self):
        """Setup custom product attributes for motor parts"""
        attributes = [
            ('part_number', 'Part Number', 'text'),
            ('call_out_order', 'Call Out Order', 'integer'),
            ('unit_qty', 'Unit Quantity', 'text'),
            ('lr_orientation', 'L/R Orientation', 'text'),
            ('remark', 'Remark', 'richtext'),
            ('nn_note', 'NN Note', 'richtext'),
            ('svg_diagram', 'SVG Diagram', 'richtext'),
        ]
        
        for code, name, attr_type in attributes:
            attr, created = ProductAttribute.objects.get_or_create(
                product_class=self.product_class,
                code=code,
                defaults={
                    'name': name,
                    'type': attr_type,
                    'required': False,
                }
            )
            if created and self.verbosity >= 2:
                self.stdout.write(f"Created product attribute: {name}")
    
    def _create_category_hierarchy(self, serial_number):
        """Create category hierarchy: Serial -> ParentTitle -> ChildTitle"""
        try:
            # Check if serial category already exists
            serial_category = Category.objects.filter(
                name=f"Serial {serial_number.serial}"
            ).first()
            
            if not serial_category:
                # Create root category for serial number
                serial_category = Category.add_root(
                    name=f"Serial {serial_number.serial}",
                    slug=f"serial-{serial_number.serial}",
                    description=f"Parts for serial number {serial_number.serial}",
                )
                self.stats['categories_created'] += 1
                if self.verbosity >= 2:
                    self.stdout.write(f"Created serial category: {serial_category.name}")
            else:
                self.stats['categories_existing'] += 1
            
            category_map = {}
            
            # Create parent title categories
            for idx, parent_title in enumerate(serial_number.parent_titles.all(), 1):
                parent_slug = f"serial-{serial_number.serial}-parent-{idx}"
                
                # Check if parent category already exists
                parent_category = Category.objects.filter(
                    name=parent_title.title,
                    slug=parent_slug
                ).first()
                
                if not parent_category:
                    # Create as child of serial category
                    parent_category = serial_category.add_child(
                        name=parent_title.title,
                        slug=parent_slug,
                        description=f"Parent category: {parent_title.title}",
                    )
                    self.stats['categories_created'] += 1
                    if self.verbosity >= 2:
                        self.stdout.write(f"Created parent category: {parent_category.name}")
                else:
                    self.stats['categories_existing'] += 1
                
                category_map[parent_title.id] = parent_category
                
                # Create child title categories
                for child_idx, child_title in enumerate(parent_title.child_titles.all(), 1):
                    child_slug = f"serial-{serial_number.serial}-parent-{idx}-child-{child_idx}"
                    
                    # Check if child category already exists
                    child_category = Category.objects.filter(
                        name=child_title.title,
                        slug=child_slug
                    ).first()
                    
                    if not child_category:
                        # Create as child of parent category
                        child_category = parent_category.add_child(
                            name=child_title.title,
                            slug=child_slug,
                            description=f"Child category: {child_title.title}",
                        )
                        self.stats['categories_created'] += 1
                        if self.verbosity >= 2:
                            self.stdout.write(f"Created child category: {child_category.name}")
                    else:
                        self.stats['categories_existing'] += 1
                    
                    category_map[f"child_{child_title.id}"] = child_category
            
            return category_map
            
        except Exception as e:
            self.stderr.write(f"Error creating category hierarchy for {serial_number.serial}: {str(e)}")
            self.stats['errors'] += 1
            return {}
    
    def _get_price_from_pricing_data(self, part):
        """Extract price from pricing data"""
        try:
            pricing_data = PricingData.objects.filter(part_number=part).first()
            if pricing_data and pricing_data.list_price:
                # Try to convert to decimal, handle various formats
                price_str = str(pricing_data.list_price).replace('£', '').replace(',', '').strip()
                return Decimal(price_str)
        except (PricingData.DoesNotExist, InvalidOperation, ValueError):
            pass
        return None
    
    def _get_stock_info(self, part):
        """Extract stock information from pricing data"""
        try:
            pricing_data = PricingData.objects.filter(part_number=part).first()
            if pricing_data and pricing_data.stock_available:
                stock_str = str(pricing_data.stock_available).strip()
                
                # Handle different stock value formats
                if stock_str.lower() == 'nil' or stock_str == '0':
                    num_in_stock = 0
                elif stock_str.endswith('+'):
                    # For values like '10+', extract the number and use it as minimum
                    try:
                        num_in_stock = int(stock_str.replace('+', ''))
                    except ValueError:
                        num_in_stock = 10  # Default for unparseable '+' values
                else:
                    # Try to parse as regular number
                    try:
                        num_in_stock = int(float(stock_str.replace(',', '')))
                    except (ValueError, TypeError):
                        num_in_stock = 0
                
                return {
                    'num_in_stock': num_in_stock,
                    'low_stock_threshold': 5,  # Default threshold
                }
        except PricingData.DoesNotExist:
            pass
        return {'num_in_stock': 0, 'low_stock_threshold': 5}
    
    def _create_product(self, part, category):
        """Create Oscar product from Part model"""
        try:
            # Create unique UPC/SKU from part number
            upc = f"EPC-{part.part_number}"
            
            # Check if product already exists
            existing_product = Product.objects.filter(
                upc=upc
            ).first()
            
            if existing_product:
                self.stats['products_existing'] += 1
                if self.verbosity >= 2:
                    self.stdout.write(f"Product already exists: {existing_product.title}")
                
                # Check if it needs a stock record
                existing_stock = StockRecord.objects.filter(
                    product=existing_product,
                    partner=self.partner
                ).first()
                
                if not existing_stock:
                    # Create stock record for existing product
                    self._create_stock_record(existing_product, part)
                else:
                    self.stats['stock_records_existing'] += 1
                
                return existing_product
            
            # Create product
            product = Product.objects.create(
                upc=upc,
                title=f"{part.part_number} - {part.usage_name}",
                slug=f"part-{part.part_number.lower()}",
                product_class=self.product_class,
                description=part.usage_name,
                is_discountable=True,
                structure=Product.STANDALONE,
            )
            
            # Add to category
            product.categories.add(category)
            
            # Set product attributes
            self._set_product_attributes(product, part)
            
            # Create stock record
            self._create_stock_record(product, part)
            
            self.stats['products_created'] += 1
            if self.verbosity >= 2:
                self.stdout.write(f"Created product: {product.title}")
            
            return product
            
        except Exception as e:
            self.stderr.write(f"Error creating product for part {part.part_number}: {str(e)}")
            self.stats['errors'] += 1
            return None
    
    def _set_product_attributes(self, product, part):
        """Set custom attributes for the product"""
        try:
            attributes = {
                'part_number': part.part_number,
                'call_out_order': part.call_out_order,
                'unit_qty': part.unit_qty or '',
                'lr_orientation': part.lr or '',
                'remark': part.remark or '',
                'nn_note': part.nn_note or '',
                'svg_diagram': part.child_title.svg_code if part.child_title else '',
            }
            
            for code, value in attributes.items():
                if value:  # Only set non-empty values
                    attr = ProductAttribute.objects.get(
                        product_class=self.product_class,
                        code=code
                    )
                    ProductAttributeValue.objects.update_or_create(
                        product=product,
                        attribute=attr,
                        defaults={'value': value}
                    )
                    
        except Exception as e:
            self.stderr.write(f"Error setting attributes for product {product.title}: {str(e)}")
    
    def _create_stock_record(self, product, part):
        """Create stock record for the product"""
        try:
            # Check if stock record already exists
            existing_stock = StockRecord.objects.filter(
                product=product,
                partner=self.partner
            ).first()
            
            if existing_stock:
                self.stats['stock_records_existing'] += 1
                return existing_stock
            
            # Get pricing and stock info
            price = self._get_price_from_pricing_data(part)
            stock_info = self._get_stock_info(part)
            
            # Create stock record
            stock_record = StockRecord.objects.create(
                product=product,
                partner=self.partner,
                partner_sku=part.part_number,
                price=price,
                price_currency='GBP',
                num_in_stock=stock_info['num_in_stock'],
                low_stock_threshold=stock_info['low_stock_threshold'],
            )
            
            self.stats['stock_records_created'] += 1
            if self.verbosity >= 2:
                self.stdout.write(f"Created stock record for: {product.title}")
            
            return stock_record
            
        except Exception as e:
            self.stderr.write(f"Error creating stock record for product {product.title}: {str(e)}")
            self.stats['errors'] += 1
            return None
    
    def _import_serial(self, serial_number):
        """Import all data for a specific serial number"""
        self.stdout.write(f"Starting import for serial: {serial_number.serial}")
        
        try:
            with transaction.atomic():
                # Create category hierarchy
                category_map = self._create_category_hierarchy(serial_number)
                
                if not category_map:
                    self.stderr.write(f"Failed to create categories for {serial_number.serial}")
                    return False
                
                # Process all parts
                total_parts = 0
                for parent_title in serial_number.parent_titles.all():
                    for child_title in parent_title.child_titles.all():
                        child_category = category_map.get(f"child_{child_title.id}")
                        
                        if not child_category:
                            self.stderr.write(f"No category found for child title: {child_title.title}")
                            continue
                        
                        for part in child_title.parts.all():
                            if not self.dry_run:
                                self._create_product(part, child_category)
                            total_parts += 1
                
                if self.dry_run:
                    self.stdout.write(
                        self.style.WARNING(f"DRY RUN: Would process {total_parts} parts")
                    )
                    raise transaction.TransactionManagementError("Dry run - rolling back")
                
                self.stdout.write(
                    self.style.SUCCESS(f"Successfully imported serial: {serial_number.serial}")
                )
                return True
                
        except transaction.TransactionManagementError:
            if not self.dry_run:
                self.stderr.write(f"Transaction failed for serial: {serial_number.serial}")
                return False
            return True
        except Exception as e:
            self.stderr.write(f"Error importing serial {serial_number.serial}: {str(e)}")
            self.stats['errors'] += 1
            return False
    
    def _import_all(self):
        """Import all serial numbers"""
        serial_numbers = SerialNumber.objects.all()
        self.stdout.write(f"Starting import of {serial_numbers.count()} serial numbers")
        
        success_count = 0
        for serial_number in serial_numbers:
            if self._import_serial(serial_number):
                success_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(f"Import complete. Success: {success_count}/{serial_numbers.count()}")
        )
        self._print_stats()
        
        return success_count == serial_numbers.count()
    
    def _print_stats(self):
        """Print import statistics"""
        self.stdout.write(self.style.SUCCESS("=== Import Statistics ==="))
        self.stdout.write(f"Categories created: {self.stats['categories_created']}")
        self.stdout.write(f"Categories existing: {self.stats['categories_existing']}")
        self.stdout.write(f"Products created: {self.stats['products_created']}")
        self.stdout.write(f"Products existing: {self.stats['products_existing']}")
        self.stdout.write(f"Stock records created: {self.stats['stock_records_created']}")
        self.stdout.write(f"Stock records existing: {self.stats['stock_records_existing']}")
        if self.stats['errors'] > 0:
            self.stdout.write(self.style.ERROR(f"Errors: {self.stats['errors']}"))

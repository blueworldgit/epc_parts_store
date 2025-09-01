"""
Django management command to import motorpartsdata to Oscar e-commerce models.

This command migrates data from the motorpartsdata app models to Oscar's 
e-commerce models (Product, Category, StockRecord, etc.).

Usage:
    python manage.py import_to_oscar
    python manage.py import_to_oscar --serial LSH14C4C5NA129710
    python manage.py import_to_oscar --dry-run
    python manage.py import_to_oscar --verbose
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, connection
from django.db.models import Q
from django.utils import timezone
import logging
import argparse
from collections import defaultdict

# Import models
from motorpartsdata.models import SerialNumber, ParentTitle, ChildTitle, Part, PricingData
from oscar.apps.catalogue.models import Product, ProductClass, Category
from oscar.apps.partner.models import Partner, StockRecord
from oscar.core.loading import get_model

# Set up logging
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Import data from motorpartsdata models to Oscar e-commerce models'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dry_run = False
        self.verbose = False
        self.stats = {
            'categories_created': 0,
            'categories_existing': 0,
            'products_created': 0,
            'products_existing': 0,
            'stock_created': 0,
            'stock_unchanged': 0,
            'errors': 0
        }

    def add_arguments(self, parser):
        parser.add_argument(
            '--serial',
            type=str,
            help='Import only the specified serial number'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be imported without making changes'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose output'
        )

    def handle(self, *args, **options):
        self.dry_run = options['dry_run']
        self.verbose = options['verbose']
        
        if self.dry_run:
            self.stdout.write(
                self.style.WARNING("DRY RUN MODE - No changes will be made")
            )

        try:
            # Check database connection
            self._verify_database_connection()
            
            # DUPLICATE PREVENTION: Show existing data counts before import
            self._show_existing_data_summary()
            
            # Get or create default partner
            partner = self._get_or_create_partner()
            
            # Get or create product class
            product_class = self._get_or_create_product_class()
            
            # Import data
            if options['serial']:
                self._import_single_serial(options['serial'], partner, product_class)
            else:
                self._import_all_serials(partner, product_class)
                
            # Print final statistics
            self._print_final_stats()
            
        except Exception as e:
            logger.error(f"Import failed: {e}")
            raise CommandError(f"Import failed: {e}")

    def _show_existing_data_summary(self):
        """Show summary of existing data to help identify potential duplicates"""
        if not self.dry_run:
            self.stdout.write("📊 EXISTING DATA SUMMARY:")
            
            # Count existing Oscar data
            category_count = Category.objects.count()
            product_count = Product.objects.count()
            stock_count = StockRecord.objects.count()
            
            self.stdout.write(f"   Existing Categories: {category_count}")
            self.stdout.write(f"   Existing Products: {product_count}")
            self.stdout.write(f"   Existing Stock Records: {stock_count}")
            
            # Count motorpartsdata
            serial_count = SerialNumber.objects.count()
            part_count = Part.objects.count()
            pricing_count = PricingData.objects.count()
            
            self.stdout.write(f"   Source Serials: {serial_count}")
            self.stdout.write(f"   Source Parts: {part_count}")
            self.stdout.write(f"   Source Pricing Records: {pricing_count}")
            self.stdout.write("=" * 60)

    def _verify_database_connection(self):
        """Verify database connection and print connection info"""
        db_settings = connection.settings_dict
        
        self.stdout.write("=" * 60)
        self.stdout.write("🏠 Database Name: {}".format(db_settings['NAME']))
        self.stdout.write("🌐 Database Host: {}".format(db_settings['HOST']))
        self.stdout.write("👤 Database User: {}".format(db_settings['USER']))
        self.stdout.write("🔌 Database Port: {}".format(db_settings['PORT']))
        self.stdout.write("🔧 Database Engine: {}".format(db_settings['ENGINE']))
        
        # Test actual connection
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT current_database(), current_user, inet_server_addr(), inet_server_port()"
            )
            db_name, db_user, db_host, db_port = cursor.fetchone()
            
        self.stdout.write("✅ ACTUAL CONNECTION:")
        self.stdout.write("   Database: {}".format(db_name))
        self.stdout.write("   User: {}".format(db_user))
        self.stdout.write("   Host: {}".format(db_host or 'localhost'))
        self.stdout.write("   Port: {}".format(db_port))
        self.stdout.write("=" * 60)

    def _get_or_create_partner(self):
        """Get or create the default partner"""
        if not self.dry_run:
            partner, created = Partner.objects.get_or_create(
                name='Default Partner',
                defaults={'code': 'default'}
            )
            if created and self.verbose:
                self.stdout.write("Created default partner")
            return partner
        else:
            # In dry run, just return a mock partner
            return Partner(name='Default Partner', code='default')

    def _get_or_create_product_class(self):
        """Get or create the default product class"""
        if not self.dry_run:
            product_class, created = ProductClass.objects.get_or_create(
                name='Motor Parts',
                defaults={'slug': 'motor-parts'}
            )
            if created and self.verbose:
                self.stdout.write("Created motor parts product class")
            return product_class
        else:
            # In dry run, just return a mock product class
            return ProductClass(name='Motor Parts', slug='motor-parts')

    def _import_single_serial(self, serial_number, partner, product_class):
        """Import a single serial number"""
        try:
            serial = SerialNumber.objects.get(serial=serial_number)
            self.stdout.write(f"Starting import for serial: {serial_number}")
            self._process_serial(serial, partner, product_class)
            self.stdout.write(
                self.style.SUCCESS(f"Successfully imported serial: {serial_number}")
            )
        except SerialNumber.DoesNotExist:
            raise CommandError(f"Serial number '{serial_number}' not found")

    def _import_all_serials(self, partner, product_class):
        """Import all serial numbers with duplicate prevention"""
        serials = SerialNumber.objects.all()
        total = serials.count()
        
        self.stdout.write(f"Starting import of {total} serial numbers")
        
        # DUPLICATE PREVENTION: Track processed serials to avoid re-processing
        processed_serials = set()
        
        for i, serial in enumerate(serials, 1):
            # Skip if already processed (duplicate prevention)
            if serial.serial in processed_serials:
                if self.verbose:
                    self.stdout.write(f"Skipping duplicate serial: {serial.serial}")
                continue
            
            processed_serials.add(serial.serial)
            
            if self.verbose:
                self.stdout.write(f"Processing serial {i}/{total}: {serial.serial}")
            
            try:
                self._process_serial(serial, partner, product_class)
                if not self.verbose:
                    # Show progress every 10 serials
                    if i % 10 == 0 or i == total:
                        self.stdout.write(f"Processed {i}/{total} serials")
            except Exception as e:
                self.stats['errors'] += 1
                logger.error(f"Error processing serial {serial.serial}: {e}")
                if self.verbose:
                    self.stdout.write(
                        self.style.ERROR(f"Error processing {serial.serial}: {e}")
                    )

        self.stdout.write(
            self.style.SUCCESS(f"Import complete. Success: {total - self.stats['errors']}/{total}")
        )

    def _process_serial(self, serial, partner, product_class):
        """Process a single serial number and its parts"""
        # Get all parent titles for this serial
        parent_titles = ParentTitle.objects.filter(serial_number=serial)
        
        for parent_title in parent_titles:
            # Get all child titles under this parent
            child_titles = ChildTitle.objects.filter(parent=parent_title)
            
            for child_title in child_titles:
                # Create/get Oscar category for this child title
                oscar_category = self._create_category(parent_title, child_title, serial)
                
                # Get all parts in this child title
                parts = Part.objects.filter(child_title=child_title)
                
                for part in parts:
                    self._create_product_and_stock(part, oscar_category, partner, product_class)

    def _create_category(self, parent_title, child_title, serial):
        """Create or get Oscar category from parent and child titles - prevents duplicates"""
        category_name = f"{serial.serial} - {parent_title.title} - {child_title.title}"
        
        if self.dry_run:
            if self.verbose:
                self.stdout.write(f"Would create category: {category_name}")
            return Category(name=category_name)
        
        # Create slug safely
        safe_slug = f"{serial.serial}-{parent_title.title}-{child_title.title}".lower()
        safe_slug = safe_slug.replace(' ', '-').replace('/', '-').replace('\\', '-')
        safe_slug = ''.join(c for c in safe_slug if c.isalnum() or c == '-')[:100]  # Limit length
        
        # DUPLICATE PREVENTION: Check if category already exists by name OR slug
        existing_category = Category.objects.filter(
            Q(name=category_name) | Q(slug=safe_slug)
        ).first()
        
        if existing_category:
            self.stats['categories_existing'] += 1
            if self.verbose:
                self.stdout.write(f"Found existing category: {category_name}")
            return existing_category
        
        # DUPLICATE PREVENTION: Double-check by searching for similar names
        similar_categories = Category.objects.filter(
            name__icontains=f"{serial.serial} - {parent_title.title}"
        )
        
        for similar in similar_categories:
            if similar.name == category_name:
                self.stats['categories_existing'] += 1
                if self.verbose:
                    self.stdout.write(f"Found duplicate category via search: {category_name}")
                return similar
        
        # Create new category using Oscar's tree methods
        try:
            # Ensure unique slug by adding counter if needed
            original_slug = safe_slug
            counter = 1
            while Category.objects.filter(slug=safe_slug).exists():
                safe_slug = f"{original_slug}-{counter}"
                counter += 1
            
            category = Category.add_root(
                name=category_name,
                slug=safe_slug
            )
            self.stats['categories_created'] += 1
            if self.verbose:
                self.stdout.write(f"Created category: {category_name}")
            return category
        except Exception as e:
            # Fallback: try to find existing or create with basic fields
            if self.verbose:
                self.stdout.write(f"Error creating category with add_root: {e}")
            category, created = Category.objects.get_or_create(
                name=category_name,
                defaults={'slug': safe_slug}
            )
            if created:
                self.stats['categories_created'] += 1
            else:
                self.stats['categories_existing'] += 1
            return category

    def _create_product_and_stock(self, part, category, partner, product_class):
        """Create or update Oscar product and stock record - prevents duplicates"""
        if self.dry_run:
            if self.verbose:
                self.stdout.write(f"Would create product: {part.part_number}")
            return
        
        # DUPLICATE PREVENTION: Check for existing product by UPC (part number)
        existing_product = Product.objects.filter(upc=part.part_number).first()
        
        if existing_product:
            # Product exists, just ensure it's in the category
            if category not in existing_product.categories.all():
                existing_product.categories.add(category)
                if self.verbose:
                    self.stdout.write(f"Added existing product {part.part_number} to category")
            
            self.stats['products_existing'] += 1
            product = existing_product
        else:
            # DUPLICATE PREVENTION: Check by title as well in case UPC is missing
            similar_products = Product.objects.filter(
                title__icontains=part.part_number
            )
            
            duplicate_found = False
            for similar in similar_products:
                if similar.upc == part.part_number or similar.title == (part.usage_name or part.part_number):
                    product = similar
                    product.categories.add(category)
                    self.stats['products_existing'] += 1
                    duplicate_found = True
                    if self.verbose:
                        self.stdout.write(f"Found duplicate product via search: {part.part_number}")
                    break
            
            if not duplicate_found:
                # Create new product
                product = Product.objects.create(
                    upc=part.part_number,
                    title=part.usage_name or part.part_number,
                    product_class=product_class,
                    structure=Product.STANDALONE,
                )
                
                self.stats['products_created'] += 1
                # Add to category
                product.categories.add(category)
                if self.verbose:
                    self.stdout.write(f"Created product: {part.part_number}")
        
        # Create or update stock record
        self._create_stock_record(part, product, partner)

    def _create_stock_record(self, part, product, partner):
        """Create or update stock record with pricing data - prevents duplicates"""
        # Get pricing and stock info
        price = self._get_price_from_pricing_data(part)
        stock_quantity = self._get_stock_info(part)
        
        if self.verbose:
            self.stdout.write(f"Price for {part.part_number}: £{price}")
            self.stdout.write(f"Stock for {part.part_number}: {stock_quantity}")
        
        # DUPLICATE PREVENTION: Check for existing stock record by multiple criteria
        existing_stock = StockRecord.objects.filter(
            Q(product=product, partner=partner) | 
            Q(partner_sku=part.part_number, partner=partner) |
            Q(product=product, partner_sku=part.part_number)
        ).first()
        
        if existing_stock:
            # Update existing stock record
            updated = False
            if existing_stock.price != price:
                existing_stock.price = price
                updated = True
            if existing_stock.num_in_stock != stock_quantity:
                existing_stock.num_in_stock = stock_quantity
                updated = True
            # Ensure partner_sku is set correctly
            if existing_stock.partner_sku != part.part_number:
                existing_stock.partner_sku = part.part_number
                updated = True
                
            if updated:
                existing_stock.save()
                self.stats['stock_created'] += 1  # Count as updated
                if self.verbose:
                    self.stdout.write(f"Updated stock record for {part.part_number}")
            else:
                self.stats['stock_unchanged'] += 1
                if self.verbose:
                    self.stdout.write(f"Stock record unchanged for {part.part_number}")
        else:
            # DUPLICATE PREVENTION: Final check for any stock record with same SKU
            sku_duplicate = StockRecord.objects.filter(partner_sku=part.part_number).first()
            
            if sku_duplicate:
                # Update the duplicate instead of creating new one
                sku_duplicate.product = product
                sku_duplicate.partner = partner
                sku_duplicate.price = price
                sku_duplicate.num_in_stock = stock_quantity
                sku_duplicate.save()
                
                self.stats['stock_created'] += 1
                if self.verbose:
                    self.stdout.write(f"Updated duplicate stock record for {part.part_number}")
            else:
                # Create new stock record
                stock_record = StockRecord.objects.create(
                    product=product,
                    partner=partner,
                    partner_sku=part.part_number,
                    price=price,
                    num_in_stock=stock_quantity,
                )
                self.stats['stock_created'] += 1
                
                if self.verbose:
                    self.stdout.write(f"Created stock record for {part.part_number}")

    def _get_price_from_pricing_data(self, part):
        """Get price from PricingData model"""
        try:
            pricing_data = PricingData.objects.filter(part_number=part).first()
            if pricing_data and pricing_data.list_price:
                price = float(pricing_data.list_price)
                if self.verbose:
                    self.stdout.write(f"Found pricing data for {part.part_number}: £{price}")
                return price
            else:
                if self.verbose:
                    self.stdout.write(f"No pricing data found for {part.part_number}")
                return 0.00
        except Exception as e:
            if self.verbose:
                self.stdout.write(f"Error getting price for {part.part_number}: {e}")
            return 0.00

    def _get_stock_info(self, part):
        """Get stock quantity from PricingData model"""
        try:
            pricing_data = PricingData.objects.filter(part_number=part).first()
            if pricing_data and hasattr(pricing_data, 'stock_quantity'):
                stock = int(pricing_data.stock_quantity or 0)
                if self.verbose:
                    self.stdout.write(f"Found stock data for {part.part_number}: {stock}")
                return stock
            else:
                # Default stock quantity if no data
                if self.verbose:
                    self.stdout.write(f"No stock data found for {part.part_number}, using default")
                return 10
        except Exception as e:
            if self.verbose:
                self.stdout.write(f"Error getting stock for {part.part_number}: {e}")
            return 10

    def _print_final_stats(self):
        """Print final import statistics"""
        self.stdout.write("=== Import Statistics ===")
        self.stdout.write(f"Categories created: {self.stats['categories_created']}")
        self.stdout.write(f"Categories existing: {self.stats['categories_existing']}")
        self.stdout.write(f"Products created: {self.stats['products_created']}")
        self.stdout.write(f"Products existing: {self.stats['products_existing']}")
        self.stdout.write(f"Stock records created/updated: {self.stats['stock_created']}")
        self.stdout.write(f"Stock records unchanged: {self.stats['stock_unchanged']}")
        self.stdout.write(f"Errors: {self.stats['errors']}")
        
        # Database verification for specific part
        self._verify_database_final()

    def _verify_database_final(self):
        """Final database verification"""
        with connection.cursor() as cursor:
            self.stdout.write("🗄️ FINAL DATABASE VERIFICATION:")
            cursor.execute("SELECT current_database()")
            db_name = cursor.fetchone()[0]
            self.stdout.write(f"   All operations performed on database: {db_name}")
            
            # Check C00112285 specifically
            cursor.execute("SELECT COUNT(*) FROM partner_stockrecord WHERE partner_sku LIKE 'C00112285';")
            count = cursor.fetchone()[0]
            self.stdout.write(f"   C00112285 stock records in database: {count}")
            
            # Show available price columns
            cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'partner_stockrecord' AND column_name LIKE '%price%';")
            price_columns = cursor.fetchall()
            price_column_names = [col[0] for col in price_columns]
            self.stdout.write(f"   Available price columns: {price_column_names}")
            
            # Show actual data for C00112285 if it exists
            if 'price' in price_column_names:
                cursor.execute("SELECT num_in_stock, price FROM partner_stockrecord WHERE partner_sku = 'C00112285' LIMIT 1;")
                result = cursor.fetchone()
                if result:
                    stock, price = result
                    self.stdout.write(f"   C00112285 current data: Stock={stock}, Price=£{price}")
            else:
                cursor.execute("SELECT num_in_stock FROM partner_stockrecord WHERE partner_sku = 'C00112285' LIMIT 1;")
                result = cursor.fetchone()
                if result:
                    stock = result[0]
                    self.stdout.write(f"   C00112285 current stock: {stock}")

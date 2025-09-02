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
        self.log_file = None
        self.stats = {
            'categories_created': 0,
            'categories_existing': 0,
            'products_created': 0,
            'products_existing': 0,
            'stock_created': 0,
            'stock_unchanged': 0,
            'errors': 0,
            'pricing_errors': 0,
            'stock_errors': 0,
            'validation_errors': 0
        }

    def _setup_file_logging(self):
        """Set up file logging with timestamped filename"""
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if self.dry_run:
            log_filename = f'import_to_oscar_dryrun_{timestamp}.log'
        else:
            log_filename = f'import_to_oscar_{timestamp}.log'
        
        self.log_file = log_filename
        
        # Create file handler
        file_handler = logging.FileHandler(log_filename, mode='w', encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(file_handler)
        logger.setLevel(logging.INFO)
        
        # Log initial setup
        logger.info("=" * 60)
        logger.info(f"IMPORT TO OSCAR LOG - {'DRY RUN' if self.dry_run else 'LIVE RUN'}")
        logger.info("=" * 60)
        
        self.stdout.write(f"📝 Logging to file: {log_filename}")
        return log_filename

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
        
        # Set up file logging first
        log_file = self._setup_file_logging()
        
        if self.dry_run:
            self.stdout.write(
                self.style.WARNING("DRY RUN MODE - No changes will be made")
            )
            logger.info("DRY RUN MODE - No changes will be made")

        try:
            # Log command start
            logger.info(f"Import command started with options: {options}")
            
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
                logger.info(f"Starting single serial import: {options['serial']}")
                self._import_single_serial(options['serial'], partner, product_class)
            else:
                logger.info("Starting full import of all serials")
                self._import_all_serials(partner, product_class)
                
            # Print final statistics
            self._print_final_stats()
            
            logger.info("Import completed successfully")
            self.stdout.write(f"📝 Full log saved to: {log_file}")
            
        except Exception as e:
            logger.error(f"Import failed: {e}")
            self.stdout.write(f"❌ Error logged to: {log_file}")
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
        
        # Log database connection info
        logger.info(f"Database Name: {db_settings['NAME']}")
        logger.info(f"Database Host: {db_settings['HOST']}")
        logger.info(f"Database User: {db_settings['USER']}")
        logger.info(f"Database Port: {db_settings['PORT']}")
        logger.info(f"Database Engine: {db_settings['ENGINE']}")
        
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
        
        # Log actual connection details
        logger.info(f"ACTUAL CONNECTION - Database: {db_name}, User: {db_user}, Host: {db_host}, Port: {db_port}")

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
        """Process a single serial number and its parts using proper category hierarchy"""
        try:
            # Create proper category hierarchy: Vehicle Brand -> Serial -> Parent -> Child
            category_map = self._create_category_hierarchy(serial)
            
            if self.dry_run:
                # In dry run, just count what we would do
                parent_titles = ParentTitle.objects.filter(serial_number=serial)
                for parent_title in parent_titles:
                    child_titles = ChildTitle.objects.filter(parent=parent_title)
                    for child_title in child_titles:
                        parts = Part.objects.filter(child_title=child_title)
                        for part in parts:
                            if self.verbose:
                                self.stdout.write(f"Would create product: {part.part_number}")
                return
            
            # Process parts and assign them to appropriate categories
            for parent_title in ParentTitle.objects.filter(serial_number=serial):
                for child_title in ChildTitle.objects.filter(parent=parent_title):
                    # Get the category for this child title
                    oscar_category = category_map.get(child_title.id)
                    if not oscar_category:
                        logger.warning(f"No category found for child title: {child_title.title}")
                        continue
                    
                    # Get all parts in this child title
                    parts = Part.objects.filter(child_title=child_title)
                    for part in parts:
                        self._create_product_and_stock(part, oscar_category, partner, product_class)
                        
        except Exception as e:
            logger.error(f"Error processing serial {serial.serial}: {e}")
            self.stats['errors'] += 1
            raise

    def _get_or_create_vehicle_category(self, brand_name):
        """Get existing vehicle category or create if doesn't exist"""
        try:
            category = Category.objects.get(name=brand_name, depth=1)
            return category
        except Category.DoesNotExist:
            # Create new category if it doesn't exist
            category = Category.add_root(name=brand_name, slug=brand_name.lower())
            return category

    def _get_or_create_serial_category(self, serial_number, vehicle_category):
        """Create serial number category under the vehicle category"""
        serial_name = f"Serial {serial_number}"
        serial_slug = f"serial-{serial_number.lower().replace('_', '-')}"
        
        # Check if serial category already exists under this vehicle
        for child in vehicle_category.get_children():
            if child.name == serial_name:
                return child
        
        # Create new serial category under vehicle category
        serial_category = vehicle_category.add_child(
            name=serial_name,
            slug=serial_slug
        )
        return serial_category

    def _create_category_hierarchy(self, serial_number):
        """Create proper category hierarchy: Vehicle Brand -> Serial -> ParentTitle -> ChildTitle"""
        
        # Get or create vehicle category (Maxus, Peugeot, etc.)
        vehicle_category = self._get_or_create_vehicle_category(serial_number.vehicle_brand)
        logger.info(f"Using vehicle category: {vehicle_category.name}")
        if self.verbose:
            self.stdout.write(f"Using vehicle category: {vehicle_category.name}")
        
        # Get or create serial category under vehicle category
        serial_category = self._get_or_create_serial_category(serial_number.serial, vehicle_category)
        logger.info(f"Using serial category: {serial_category.name}")
        if self.verbose:
            self.stdout.write(f"Using serial category: {serial_category.name}")
        
        if self.dry_run:
            return {}
        
        category_map = {}
        
        # Create parent title categories under serial category
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
                logger.info(f"Created parent category: {parent_category.name}")
                if self.verbose:
                    self.stdout.write(f"Created parent category: {parent_category.name}")
            else:
                self.stats['categories_existing'] += 1
            
            category_map[parent_title.id] = parent_category
            
            # Create child title categories under parent category
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
                    logger.info(f"Created child category: {child_category.name}")
                    if self.verbose:
                        self.stdout.write(f"Created child category: {child_category.name}")
                else:
                    self.stats['categories_existing'] += 1
                
                category_map[child_title.id] = child_category
        
        return category_map

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
                logger.info(f"Updated stock record for {part.part_number}: price=£{price}, stock={stock_quantity}")
                if self.verbose:
                    self.stdout.write(f"Updated stock record for {part.part_number}")
            else:
                self.stats['stock_unchanged'] += 1
                logger.info(f"Stock record unchanged for {part.part_number}")
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
        """Get price from PricingData model with strict error handling"""
        try:
            pricing_data = PricingData.objects.filter(part_number=part).first()
            
            if not pricing_data:
                # ERROR: No pricing data found - log as error and return 0.00
                error_msg = f"No pricing data found for part {part.part_number}"
                logger.error(error_msg)
                self.stats['errors'] += 1
                self.stats['pricing_errors'] += 1
                if self.verbose:
                    self.stdout.write(self.style.ERROR(f"❌ {error_msg}"))
                return 0.00
            
            if pricing_data.list_price:
                try:
                    # Clean and validate the price string
                    price_str = str(pricing_data.list_price).strip()
                    
                    # Remove common currency symbols and commas
                    price_str = price_str.replace('£', '').replace('$', '').replace(',', '').strip()
                    
                    # Validate it's not empty after cleaning
                    if not price_str:
                        error_msg = f"Empty price after cleaning for part {part.part_number}"
                        logger.error(error_msg)
                        self.stats['errors'] += 1
                        self.stats['pricing_errors'] += 1
                        if self.verbose:
                            self.stdout.write(self.style.ERROR(f"❌ {error_msg}"))
                        return 0.00
                    
                    # Parse as float and validate
                    price = float(price_str)
                    
                    # Validate price is not negative
                    if price < 0:
                        error_msg = f"Negative price {price} for part {part.part_number}, setting to 0.00"
                        logger.warning(error_msg)
                        self.stats['validation_errors'] += 1
                        if self.verbose:
                            self.stdout.write(self.style.WARNING(f"⚠️ {error_msg}"))
                        return 0.00
                    
                    # Validate price is reasonable (not too high)
                    if price > 99999.99:
                        error_msg = f"Unreasonably high price {price} for part {part.part_number}, setting to 0.00"
                        logger.warning(error_msg)
                        self.stats['validation_errors'] += 1
                        if self.verbose:
                            self.stdout.write(self.style.WARNING(f"⚠️ {error_msg}"))
                        return 0.00
                    
                    if self.verbose:
                        self.stdout.write(f"✅ Valid price data for {part.part_number}: £{price}")
                    return round(price, 2)  # Round to 2 decimal places
                    
                except (ValueError, TypeError) as e:
                    # ERROR: Invalid price format - log as error and return 0.00
                    error_msg = f"Invalid price format '{pricing_data.list_price}' for part {part.part_number}: {str(e)}"
                    logger.error(error_msg)
                    self.stats['errors'] += 1
                    self.stats['pricing_errors'] += 1
                    if self.verbose:
                        self.stdout.write(self.style.ERROR(f"❌ {error_msg}"))
                    return 0.00
            else:
                # ERROR: No list_price field or empty value - log as error and return 0.00
                error_msg = f"No list_price field or empty value for part {part.part_number}"
                logger.error(error_msg)
                self.stats['errors'] += 1
                self.stats['pricing_errors'] += 1
                if self.verbose:
                    self.stdout.write(self.style.ERROR(f"❌ {error_msg}"))
                return 0.00
                
        except Exception as e:
            # ERROR: Unexpected exception - log as error and return 0.00
            error_msg = f"Exception getting price for {part.part_number}: {str(e)}"
            logger.error(error_msg)
            self.stats['errors'] += 1
            self.stats['pricing_errors'] += 1
            if self.verbose:
                self.stdout.write(self.style.ERROR(f"❌ {error_msg}"))
            return 0.00

    def _get_stock_info(self, part):
        """Get stock quantity from PricingData model with strict error handling"""
        try:
            pricing_data = PricingData.objects.filter(part_number=part).first()
            
            if not pricing_data:
                # ERROR: No pricing data found - log as error and return 0
                error_msg = f"No pricing data found for part {part.part_number}"
                logger.error(error_msg)
                self.stats['errors'] += 1
                self.stats['stock_errors'] += 1
                if self.verbose:
                    self.stdout.write(self.style.ERROR(f"❌ {error_msg}"))
                return 0
            
            # Check for stock_available field (correct field name in PricingData model)
            if hasattr(pricing_data, 'stock_available') and pricing_data.stock_available:
                stock_str = str(pricing_data.stock_available).strip()
                
                # Handle different stock value formats with proper validation
                if stock_str.lower() == 'nil' or stock_str == '0':
                    stock = 0
                elif stock_str.endswith('+'):
                    try:
                        # Extract number from "10+" format and add 1 for "+" indicator
                        base_stock = int(stock_str.replace('+', ''))
                        stock = base_stock + 1  # "10+" becomes 11, "5+" becomes 6, etc.
                        if self.verbose:
                            self.stdout.write(f"📦 Stock '{stock_str}' converted to {stock} for {part.part_number}")
                    except ValueError:
                        # ERROR: Invalid '+' format - log as error and return 0
                        error_msg = f"Invalid stock format '{stock_str}' for part {part.part_number}"
                        logger.error(error_msg)
                        self.stats['errors'] += 1
                        self.stats['stock_errors'] += 1
                        if self.verbose:
                            self.stdout.write(self.style.ERROR(f"❌ {error_msg}"))
                        return 0
                else:
                    try:
                        # Parse regular numeric values (handle commas)
                        stock = int(float(stock_str.replace(',', '')))
                    except (ValueError, TypeError):
                        # ERROR: Invalid stock format - log as error and return 0
                        error_msg = f"Invalid stock format '{stock_str}' for part {part.part_number}"
                        logger.error(error_msg)
                        self.stats['errors'] += 1
                        self.stats['stock_errors'] += 1
                        if self.verbose:
                            self.stdout.write(self.style.ERROR(f"❌ {error_msg}"))
                        return 0
                
                # Validate stock is not negative
                if stock < 0:
                    error_msg = f"Negative stock value {stock} for part {part.part_number}, setting to 0"
                    logger.warning(error_msg)
                    self.stats['validation_errors'] += 1
                    if self.verbose:
                        self.stdout.write(self.style.WARNING(f"⚠️ {error_msg}"))
                    return 0
                
                if self.verbose:
                    self.stdout.write(f"✅ Valid stock data for {part.part_number}: {stock}")
                return stock
            else:
                # ERROR: No stock_available field or empty value - log as error and return 0
                error_msg = f"No stock_available field or empty value for part {part.part_number}"
                logger.error(error_msg)
                self.stats['errors'] += 1
                self.stats['stock_errors'] += 1
                if self.verbose:
                    self.stdout.write(self.style.ERROR(f"❌ {error_msg}"))
                return 0
                
        except Exception as e:
            # ERROR: Unexpected exception - log as error and return 0
            error_msg = f"Exception getting stock for {part.part_number}: {str(e)}"
            logger.error(error_msg)
            self.stats['errors'] += 1
            self.stats['stock_errors'] += 1
            if self.verbose:
                self.stdout.write(self.style.ERROR(f"❌ {error_msg}"))
            return 0

    def _print_final_stats(self):
        """Print final import statistics with detailed error breakdown"""
        self.stdout.write("=== Import Statistics ===")
        self.stdout.write(f"Categories created: {self.stats['categories_created']}")
        self.stdout.write(f"Categories existing: {self.stats['categories_existing']}")
        self.stdout.write(f"Products created: {self.stats['products_created']}")
        self.stdout.write(f"Products existing: {self.stats['products_existing']}")
        self.stdout.write(f"Stock records created/updated: {self.stats['stock_created']}")
        self.stdout.write(f"Stock records unchanged: {self.stats['stock_unchanged']}")
        self.stdout.write("=== Error Breakdown ===")
        self.stdout.write(f"Total errors: {self.stats['errors']}")
        self.stdout.write(f"  └─ Pricing errors: {self.stats['pricing_errors']}")
        self.stdout.write(f"  └─ Stock errors: {self.stats['stock_errors']}")
        self.stdout.write(f"  └─ Validation errors: {self.stats['validation_errors']}")
        
        # Log statistics
        logger.info("=== FINAL IMPORT STATISTICS ===")
        logger.info(f"Categories created: {self.stats['categories_created']}")
        logger.info(f"Categories existing: {self.stats['categories_existing']}")
        logger.info(f"Products created: {self.stats['products_created']}")
        logger.info(f"Products existing: {self.stats['products_existing']}")
        logger.info(f"Stock records created/updated: {self.stats['stock_created']}")
        logger.info(f"Stock records unchanged: {self.stats['stock_unchanged']}")
        logger.info("=== ERROR BREAKDOWN ===")
        logger.info(f"Total errors: {self.stats['errors']}")
        logger.info(f"  └─ Pricing errors: {self.stats['pricing_errors']}")
        logger.info(f"  └─ Stock errors: {self.stats['stock_errors']}")
        logger.info(f"  └─ Validation errors: {self.stats['validation_errors']}")
        
        # Quality metrics
        total_processed = self.stats['products_created'] + self.stats['products_existing']
        if total_processed > 0:
            error_rate = (self.stats['errors'] / total_processed) * 100
            self.stdout.write(f"Data quality: {error_rate:.1f}% error rate")
            logger.info(f"Data quality: {error_rate:.1f}% error rate")
        
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

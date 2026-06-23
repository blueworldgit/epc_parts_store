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
from django.core.management import call_command
from django.db import transaction, connection
from django.db.models import Q
from django.db.models.signals import post_save
from django.utils import timezone
import logging
import argparse
from collections import defaultdict

# Import models
from motorpartsdata.models import SerialNumber, ParentTitle, ChildTitle, Part, PricingData
from oscar.apps.catalogue.models import Product, ProductClass, Category, ProductAttribute, ProductAttributeValue
from oscar.apps.partner.models import Partner, StockRecord
from oscar.core.loading import get_model

# Set up logging
logger = logging.getLogger(__name__)

# Try to import Oscar's customer alerts signal (might not be enabled in all installations)
try:
    from oscar.apps.customer.alerts import receivers as alerts_receivers
    OSCAR_ALERTS_AVAILABLE = True
except ImportError:
    OSCAR_ALERTS_AVAILABLE = False
    alerts_receivers = None

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
            'parts_processed': 0,
            'parts_skipped': 0,
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
        parser.add_argument(
            '--reset-processed',
            action='store_true',
            help='Reset all parts to unprocessed (for testing/re-import)'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=1500,
            help='Maximum number of parts to process in one run (default: 1500)'
        )

    def handle(self, *args, **options):
        self.dry_run = options['dry_run']
        self.verbose = options['verbose']
        reset_processed = options.get('reset_processed', False)
        self.batch_size = options.get('batch_size', 1500)
        
        # Set up file logging first
        log_file = self._setup_file_logging()
        
        if self.dry_run:
            self.stdout.write(
                self.style.WARNING("DRY RUN MODE - No changes will be made")
            )
            logger.info("DRY RUN MODE - No changes will be made")
        
        # Handle reset flag
        if reset_processed:
            if not self.dry_run:
                reset_count = Part.objects.filter(oscar_imported=True).update(
                    oscar_imported=False, 
                    oscar_imported_at=None
                )
                self.stdout.write(self.style.SUCCESS(f"✅ Reset {reset_count} parts to unprocessed"))
                logger.info(f"Reset {reset_count} parts to unprocessed")
            else:
                reset_count = Part.objects.filter(oscar_imported=True).count()
                self.stdout.write(f"Would reset {reset_count} parts to unprocessed")
            return

        # Disconnect Oscar customer alerts signal to prevent performance issues during import
        signal_was_connected = False
        if OSCAR_ALERTS_AVAILABLE and hasattr(alerts_receivers, 'send_product_alerts'):
            try:
                post_save.disconnect(alerts_receivers.send_product_alerts, sender=StockRecord)
                signal_was_connected = True
                self.stdout.write("🔕 Disabled Oscar product alerts during import for better performance")
                logger.info("Disconnected Oscar product alerts signal")
            except Exception as e:
                logger.warning(f"Could not disconnect alerts signal: {e}")

        try:
            # Log command start
            logger.info(f"Import command started with options: {options}")
            
            # Check database connection
            self._verify_database_connection()
            
            # DUPLICATE PREVENTION: Show existing data counts before import
            self._show_existing_data_summary()
            
            # Show unprocessed parts summary
            self._show_unprocessed_parts_summary()
            
            # Get or create default partner
            partner = self._get_or_create_partner()
            
            # Get or create product class
            product_class = self._get_or_create_product_class()
            
            # Get or create product attributes for additional part data
            product_attributes = self._get_or_create_product_attributes(product_class)
            
            # Import data
            if options['serial']:
                logger.info(f"Starting single serial import: {options['serial']}")
                self._import_single_serial(options['serial'], partner, product_class, product_attributes)
            else:
                logger.info("Starting full import of all serials")
                self._import_all_serials(partner, product_class, product_attributes)
                
            # Print final statistics
            self._print_final_stats()
            
            # DISABLED: Automatic price and weight updates after import
            # Uncomment the section below if you want to re-enable automatic price and weight updates
            """
            # Automatically update prices in Oscar after import
            if not self.dry_run:
                self.stdout.write("🔄 Running price update to synchronize with Oscar...")
                try:
                    call_command('update_prices', '--sync-to-oscar', verbosity=1 if self.verbose else 0)
                    self.stdout.write(self.style.SUCCESS("✅ Price update completed successfully"))
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"⚠️ Price update failed: {e}"))
                    logger.warning(f"Price update failed: {e}")
                
                # Automatically update all product weights based on pricing
                self.stdout.write("⚖️ Running weight update for all products...")
                try:
                    call_command('updateallweights', verbosity=1 if self.verbose else 0)
                    self.stdout.write(self.style.SUCCESS("✅ Weight update completed successfully"))
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"⚠️ Weight update failed: {e}"))
                    logger.warning(f"Weight update failed: {e}")
            else:
                self.stdout.write("🏃 Skipping price update (dry-run mode)")
                self.stdout.write("🏃 Skipping weight update (dry-run mode)")
            """
            
            # Show final completion summary (after price update)
            self._print_completion_summary()
            
            logger.info("Import completed successfully")
            self.stdout.write(f"📝 Full log saved to: {log_file}")
            
        except Exception as e:
            logger.error(f"Import failed: {e}")
            self.stdout.write(f"❌ Error logged to: {log_file}")
            raise CommandError(f"Import failed: {e}")
        finally:
            # Reconnect Oscar customer alerts signal if it was disconnected
            if signal_was_connected and OSCAR_ALERTS_AVAILABLE:
                try:
                    post_save.connect(alerts_receivers.send_product_alerts, sender=StockRecord)
                    self.stdout.write("🔔 Re-enabled Oscar product alerts")
                    logger.info("Reconnected Oscar product alerts signal")
                except Exception as e:
                    logger.warning(f"Could not reconnect alerts signal: {e}")

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
            
            # Show unprocessed parts summary
            self._show_unprocessed_parts_summary()
            
            self.stdout.write("=" * 60)

    def _show_unprocessed_parts_summary(self):
        """Show summary of parts that need processing"""
        total_parts = Part.objects.count()
        processed_parts = Part.objects.filter(oscar_imported=True).count()
        unprocessed_parts = Part.objects.filter(oscar_imported=False).count()
        
        self.stdout.write("📦 PARTS PROCESSING SUMMARY:")
        self.stdout.write(f"  Total parts in database: {total_parts}")
        self.stdout.write(f"  Already processed: {processed_parts}")
        self.stdout.write(f"  Pending processing: {unprocessed_parts}")
        
        if unprocessed_parts == 0:
            self.stdout.write(self.style.SUCCESS("✅ All parts have been processed!"))
        else:
            parts_this_batch = min(self.batch_size, unprocessed_parts)
            self.stdout.write(f"🔄 Will process {parts_this_batch} parts this batch (max batch size: {self.batch_size})")
            if unprocessed_parts > self.batch_size:
                remaining = unprocessed_parts - self.batch_size
                self.stdout.write(f"   {remaining} parts will remain for next run")
        self.stdout.write("")

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

    def _get_or_create_product_attributes(self, product_class):
        """Create or get product attributes for additional part data"""
        attributes = {}
        
        # Define the attributes we want to create
        attr_definitions = [
            ('call_out_order', 'Call Out Order', 'integer'),
            ('orientation', 'Orientation', 'text'),
            ('part_remark', 'Part Remark', 'text'),
            ('part_note', 'Part Note', 'text'),
        ]
        
        if not self.dry_run:
            for code, name, attr_type in attr_definitions:
                attr, created = ProductAttribute.objects.get_or_create(
                    code=code,
                    defaults={
                        'name': name,
                        'type': attr_type,
                        'product_class': None,  # Global attribute
                        'required': False,
                    }
                )
                attributes[code] = attr
                if created and self.verbose:
                    self.stdout.write(f"Created product attribute: {name}")
        
        return attributes

    def _import_single_serial(self, serial_number, partner, product_class, product_attributes):
        """Import a single serial number"""
        try:
            serial = SerialNumber.objects.get(serial=serial_number)
            self.stdout.write(f"Starting import for serial: {serial_number}")
            self._process_serial(serial, partner, product_class, product_attributes)
            self.stdout.write(
                self.style.SUCCESS(f"Successfully imported serial: {serial_number}")
            )
        except SerialNumber.DoesNotExist:
            raise CommandError(f"Serial number '{serial_number}' not found")

    def _import_all_serials(self, partner, product_class, product_attributes):
        """Import all serial numbers with batch processing to prevent timeouts"""
        serials = SerialNumber.objects.all()
        total = serials.count()
        
        self.stdout.write(f"Starting import of {total} serial numbers")
        
        # DUPLICATE PREVENTION: Track processed serials to avoid re-processing
        processed_serials = set()
        parts_processed_this_run = 0
        
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
                parts_before = self.stats['parts_processed']
                self._process_serial(serial, partner, product_class, product_attributes)
                parts_after = self.stats['parts_processed']
                parts_processed_this_serial = parts_after - parts_before
                parts_processed_this_run += parts_processed_this_serial
                
                # Check if we've reached the batch limit
                if parts_processed_this_run >= self.batch_size:
                    remaining_parts = Part.objects.filter(oscar_imported=False).count()
                    self.stdout.write(self.style.SUCCESS(
                        f"✅ Batch limit reached! Processed {parts_processed_this_run} parts this run."
                    ))
                    if remaining_parts > 0:
                        self.stdout.write(f"🔄 {remaining_parts} parts remaining for next run.")
                        self.stdout.write("💡 Run the command again to process the next batch.")
                    break
                
                if not self.verbose:
                    # Show progress every 10 serials
                    if i % 10 == 0 or i == total:
                        self.stdout.write(f"Processed {i}/{total} serials, {parts_processed_this_run} parts processed")
                        
            except Exception as e:
                self.stats['errors'] += 1
                logger.error(f"Error processing serial {serial.serial}: {e}")
                if self.verbose:
                    self.stdout.write(
                        self.style.ERROR(f"Error processing {serial.serial}: {e}")
                    )

        self.stdout.write(
            self.style.SUCCESS(f"Import complete. Processed {parts_processed_this_run} parts in this batch.")
        )

    def _process_serial(self, serial, partner, product_class, product_attributes):
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
                        parts = Part.objects.filter(child_title=child_title, oscar_imported=False)
                        for part in parts:
                            if self.verbose:
                                self.stdout.write(f"Would create product: {part.part_number}")
                return
            
            # Process parts and assign them to appropriate categories
            for parent_title in ParentTitle.objects.filter(serial_number=serial):
                for child_title in ChildTitle.objects.filter(parent=parent_title):
                    # Get the category for this child title
                    oscar_category = category_map.get(f"child_{child_title.id}")
                    if not oscar_category:
                        logger.warning(f"No category found for child title: {child_title.title}")
                        continue
                    
                    # Get all unprocessed parts in this child title
                    parts = Part.objects.filter(child_title=child_title, oscar_imported=False)
                    for part in parts:
                        success = self._create_product_and_stock(part, oscar_category, partner, product_class, product_attributes)
                        # Mark as imported if successful
                        if success:
                            part.oscar_imported = True
                            part.oscar_imported_at = timezone.now()
                            part.save()
                            self.stats['parts_processed'] += 1
                        else:
                            self.stats['parts_skipped'] += 1
                        
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
                
                category_map[f"child_{child_title.id}"] = child_category
        
        return category_map

    def _create_product_and_stock(self, part, category, partner, product_class, product_attributes):
        """Create or update Oscar product and stock record - prevents duplicates
        Returns True if successful, False if error occurred"""
        try:
            if self.dry_run:
                if self.verbose:
                    self.stdout.write(f"Would create product: {part.part_number}")
                return True
            
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
                
                # Skip stock/price updates for existing products to preserve manual changes
                self._save_product_attributes(product, part, product_attributes)
                return True  # Skip to avoid overwriting prices
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
            
            # Save product attributes for both new and existing products
            self._save_product_attributes(product, part, product_attributes)
            
            # Create or update stock record
            self._create_stock_record(part, product, partner)
            
            return True  # Success
            
        except Exception as e:
            logger.error(f"Failed to create product/stock for {part.part_number}: {e}")
            self.stats['errors'] += 1
            if self.verbose:
                self.stdout.write(self.style.ERROR(f"❌ Error creating {part.part_number}: {e}"))
            return False  # Failed

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

    def _save_product_attributes(self, product, part, product_attributes):
        """Save additional part data as product attributes"""
        if self.dry_run or not product_attributes:
            return
            
        # Mapping of part fields to attribute codes
        attribute_mappings = {
            'call_out_order': part.call_out_order,
            'orientation': part.lr,
            'part_remark': part.remark,
            'part_note': part.nn_note,
        }
        
        for attr_code, value in attribute_mappings.items():
            if value and attr_code in product_attributes:
                attr = product_attributes[attr_code]
                
                # Get or create the attribute value
                attr_value, created = ProductAttributeValue.objects.get_or_create(
                    product=product,
                    attribute=attr,
                    defaults={'value_text': str(value) if value else ''}
                )
                
                # Update value if it changed
                if not created and str(attr_value.value_text) != str(value):
                    attr_value.value_text = str(value)
                    attr_value.save()
                
                if self.verbose and created:
                    self.stdout.write(f"  Added attribute {attr.name}: {value}")

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
        """Get stock quantity - always return 50 for all parts"""
        if self.verbose:
            self.stdout.write(f"📦 Setting stock to 50 for {part.part_number}")
        return 50

    def _print_final_stats(self):
        """Print final import statistics with detailed error breakdown"""
        # Check if more parts remain to be processed
        remaining_parts = Part.objects.filter(oscar_imported=False).count()
        
        self.stdout.write("=== Import Statistics ===")
        self.stdout.write(f"Categories created: {self.stats['categories_created']}")
        self.stdout.write(f"Categories existing: {self.stats['categories_existing']}")
        self.stdout.write(f"Products created: {self.stats['products_created']}")
        self.stdout.write(f"Products existing: {self.stats['products_existing']}")
        self.stdout.write(f"Stock records created/updated: {self.stats['stock_created']}")
        self.stdout.write(f"Stock records unchanged: {self.stats['stock_unchanged']}")
        self.stdout.write("=== Parts Processing ===")
        self.stdout.write(f"Parts successfully processed: {self.stats['parts_processed']}")
        self.stdout.write(f"Parts skipped (errors): {self.stats['parts_skipped']}")
        
        if remaining_parts > 0:
            self.stdout.write(f"Parts remaining for next run: {remaining_parts}")
            self.stdout.write("💡 Run the command again to process the next batch.")
        else:
            self.stdout.write(self.style.SUCCESS("🎉 All parts have been processed!"))
            
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
        logger.info(f"Parts successfully processed: {self.stats['parts_processed']}")
        logger.info(f"Parts skipped (errors): {self.stats['parts_skipped']}")
        logger.info(f"Parts remaining: {remaining_parts}")
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

    def _print_completion_summary(self):
        """Print a prominent completion summary with remaining parts count"""
        remaining_parts = Part.objects.filter(oscar_imported=False).count()
        total_parts = Part.objects.count()
        processed_parts = total_parts - remaining_parts
        
        self.stdout.write("=" * 60)
        self.stdout.write("🎯 IMPORT COMPLETION SUMMARY")
        self.stdout.write("=" * 60)
        
        if remaining_parts == 0:
            self.stdout.write(self.style.SUCCESS("🎉 IMPORT COMPLETE - ALL PARTS PROCESSED!"))
            self.stdout.write(f"✅ Total parts processed: {processed_parts}/{total_parts}")
        else:
            completion_percentage = (processed_parts / total_parts) * 100
            self.stdout.write(f"📊 Progress: {processed_parts}/{total_parts} parts ({completion_percentage:.1f}% complete)")
            self.stdout.write(f"📦 Parts processed this batch: {self.stats['parts_processed']}")
            self.stdout.write("")
            self.stdout.write(self.style.WARNING(f"⏳ REMAINING TO IMPORT: {remaining_parts} parts"))
            self.stdout.write("🔄 Run the command again to process the next batch:")
            self.stdout.write(f"   python manage.py import_to_oscar --batch-size {self.batch_size}")
        
        self.stdout.write("=" * 60)

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

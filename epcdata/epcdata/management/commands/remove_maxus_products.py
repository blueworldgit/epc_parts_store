"""
Django management command to completely remove all Maxus products and associated data.
This script will clean up the database to prepare for fresh product imports.

Usage:
    python manage.py remove_maxus_products --dry-run  # See what would be deleted
    python manage.py remove_maxus_products --verbose  # Show detailed progress
    python manage.py remove_maxus_products            # Actually delete the data
"""

import logging
import os
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction
from django.db.models import Q

# Django Oscar models
from oscar.apps.catalogue.models import Product, Category
from oscar.apps.partner.models import StockRecord

# Import our models
from motorpartsdata.models import SerialNumber, ParentTitle, ChildTitle, Part, PricingData

# Set up logging
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Completely remove all Maxus products and associated data for fresh import'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dry_run = False
        self.verbose = False
        self.log_file = None
        self.stats = {
            'categories_deleted': 0,
            'products_deleted': 0,
            'stock_records_deleted': 0,
            'parts_deleted': 0,
            'child_titles_deleted': 0,
            'parent_titles_deleted': 0,
            'serials_deleted': 0,
            'pricing_data_deleted': 0,
            'errors': 0
        }

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting anything'
        )
        parser.add_argument(
            '--verbose',
            action='store_true', 
            help='Show detailed progress information'
        )
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Skip confirmation prompt (use with caution!)'
        )

    def handle(self, *args, **options):
        self.dry_run = options['dry_run']
        self.verbose = options['verbose']
        
        # Set up file logging
        self._setup_file_logging()
        
        try:
            self.stdout.write("=" * 60)
            self.stdout.write("🗑️  MAXUS PRODUCT REMOVAL SCRIPT")
            self.stdout.write("=" * 60)
            
            # Verify database connection
            self._verify_database_connection()
            
            # Show what we'll be removing
            self._show_removal_summary()
            
            # Confirmation check (unless --confirm flag is used)
            if not options.get('confirm', False) and not self.dry_run:
                self.stdout.write(self.style.WARNING("⚠️  WARNING: This will permanently delete ALL Maxus data!"))
                confirm = input("Are you sure you want to continue? Type 'DELETE MAXUS' to confirm: ")
                if confirm != 'DELETE MAXUS':
                    self.stdout.write("❌ Operation cancelled.")
                    return
            
            if self.dry_run:
                self.stdout.write(self.style.SUCCESS("🔍 DRY RUN MODE - No data will be deleted"))
            else:
                self.stdout.write(self.style.WARNING("🗑️  DELETION MODE - Data will be permanently removed"))
            
            # Perform the removal
            with transaction.atomic():
                self._remove_maxus_data()
            
            # Print final statistics
            self._print_final_stats()
            
            logger.info("Maxus removal completed successfully")
            self.stdout.write(f"📝 Full log saved to: {self.log_file}")
            
        except Exception as e:
            logger.error(f"Removal failed: {e}")
            self.stdout.write(f"❌ Error logged to: {self.log_file}")
            raise CommandError(f"Removal failed: {e}")

    def _setup_file_logging(self):
        """Set up file logging with timestamped filename"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = f"maxus_removal_{timestamp}.log"
        
        # Create file handler
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(file_handler)
        logger.setLevel(logging.INFO)

    def _verify_database_connection(self):
        """Verify database connection and print connection info"""
        db_settings = connection.settings_dict
        
        self.stdout.write("=" * 60)
        self.stdout.write("🏠 Database Name: {}".format(db_settings['NAME']))
        self.stdout.write("🌐 Database Host: {}".format(db_settings['HOST']))
        self.stdout.write("👤 Database User: {}".format(db_settings['USER']))
        self.stdout.write("=" * 60)
        
        logger.info(f"Connected to database: {db_settings['NAME']} on {db_settings['HOST']}")

    def _show_removal_summary(self):
        """Show summary of what will be removed"""
        self.stdout.write("📊 REMOVAL SUMMARY:")
        
        # Count Maxus categories
        maxus_categories = Category.objects.filter(
            Q(name__icontains='maxus') | Q(slug__icontains='maxus')
        )
        
        # Count products under Maxus categories
        maxus_products = Product.objects.filter(categories__in=maxus_categories).distinct()
        
        # Count stock records for Maxus products
        maxus_stock_records = StockRecord.objects.filter(product__in=maxus_products)
        
        # Count motorpartsdata entries (serials starting with VM)
        maxus_serials = SerialNumber.objects.filter(serial__startswith='VM')
        maxus_parent_titles = ParentTitle.objects.filter(serial_number__in=maxus_serials)
        maxus_child_titles = ChildTitle.objects.filter(parent__in=maxus_parent_titles)
        maxus_parts = Part.objects.filter(child_title__in=maxus_child_titles)
        maxus_pricing_data = PricingData.objects.filter(part_number__in=maxus_parts)
        
        self.stdout.write(f"   Maxus Categories: {maxus_categories.count()}")
        self.stdout.write(f"   Maxus Products: {maxus_products.count()}")
        self.stdout.write(f"   Stock Records: {maxus_stock_records.count()}")
        self.stdout.write(f"   Serial Numbers (VM*): {maxus_serials.count()}")
        self.stdout.write(f"   Parent Titles: {maxus_parent_titles.count()}")
        self.stdout.write(f"   Child Titles: {maxus_child_titles.count()}")
        self.stdout.write(f"   Parts: {maxus_parts.count()}")
        self.stdout.write(f"   Pricing Data: {maxus_pricing_data.count()}")
        self.stdout.write("=" * 60)

    def _remove_maxus_data(self):
        """Remove all Maxus data in the correct order to avoid foreign key constraints"""
        
        # Step 1: Remove pricing data first (has FK to Parts)
        self._remove_pricing_data()
        
        # Step 2: Remove stock records (has FK to Products)
        self._remove_stock_records()
        
        # Step 3: Remove products (has FK to Categories)
        self._remove_products()
        
        # Step 4: Remove parts (has FK to ChildTitles)
        self._remove_parts()
        
        # Step 5: Remove child titles (has FK to ParentTitles)
        self._remove_child_titles()
        
        # Step 6: Remove parent titles (has FK to SerialNumbers)
        self._remove_parent_titles()
        
        # Step 7: Remove serial numbers
        self._remove_serial_numbers()
        
        # Step 8: Remove categories last (products reference them)
        self._remove_categories()

    def _remove_pricing_data(self):
        """Remove all pricing data for Maxus parts"""
        try:
            # Get Maxus serials
            maxus_serials = SerialNumber.objects.filter(serial__startswith='VM')
            maxus_parent_titles = ParentTitle.objects.filter(serial_number__in=maxus_serials)
            maxus_child_titles = ChildTitle.objects.filter(parent__in=maxus_parent_titles)
            maxus_parts = Part.objects.filter(child_title__in=maxus_child_titles)
            
            # Get pricing data for these parts
            pricing_data_to_delete = PricingData.objects.filter(part_number__in=maxus_parts)
            count = pricing_data_to_delete.count()
            
            if self.verbose:
                self.stdout.write(f"🗑️  Removing {count} pricing data records...")
            
            if not self.dry_run:
                deleted_count = pricing_data_to_delete.delete()[0]
                self.stats['pricing_data_deleted'] = deleted_count
                logger.info(f"Deleted {deleted_count} pricing data records")
            else:
                self.stats['pricing_data_deleted'] = count
                
        except Exception as e:
            error_msg = f"Error removing pricing data: {e}"
            logger.error(error_msg)
            self.stats['errors'] += 1
            if self.verbose:
                self.stdout.write(self.style.ERROR(f"❌ {error_msg}"))

    def _remove_stock_records(self):
        """Remove all stock records for Maxus products"""
        try:
            # Get Maxus products
            maxus_categories = Category.objects.filter(
                Q(name__icontains='maxus') | Q(slug__icontains='maxus')
            )
            maxus_products = Product.objects.filter(categories__in=maxus_categories).distinct()
            
            # Get stock records for these products
            stock_records_to_delete = StockRecord.objects.filter(product__in=maxus_products)
            count = stock_records_to_delete.count()
            
            if self.verbose:
                self.stdout.write(f"🗑️  Removing {count} stock records...")
            
            if not self.dry_run:
                deleted_count = stock_records_to_delete.delete()[0]
                self.stats['stock_records_deleted'] = deleted_count
                logger.info(f"Deleted {deleted_count} stock records")
            else:
                self.stats['stock_records_deleted'] = count
                
        except Exception as e:
            error_msg = f"Error removing stock records: {e}"
            logger.error(error_msg)
            self.stats['errors'] += 1
            if self.verbose:
                self.stdout.write(self.style.ERROR(f"❌ {error_msg}"))

    def _remove_products(self):
        """Remove all Maxus products"""
        try:
            # Get Maxus products
            maxus_categories = Category.objects.filter(
                Q(name__icontains='maxus') | Q(slug__icontains='maxus')
            )
            products_to_delete = Product.objects.filter(categories__in=maxus_categories).distinct()
            count = products_to_delete.count()
            
            if self.verbose:
                self.stdout.write(f"🗑️  Removing {count} products...")
            
            if not self.dry_run:
                deleted_count = products_to_delete.delete()[0]
                self.stats['products_deleted'] = deleted_count
                logger.info(f"Deleted {deleted_count} products")
            else:
                self.stats['products_deleted'] = count
                
        except Exception as e:
            error_msg = f"Error removing products: {e}"
            logger.error(error_msg)
            self.stats['errors'] += 1
            if self.verbose:
                self.stdout.write(self.style.ERROR(f"❌ {error_msg}"))

    def _remove_parts(self):
        """Remove all Maxus parts"""
        try:
            # Get Maxus serials
            maxus_serials = SerialNumber.objects.filter(serial__startswith='VM')
            maxus_parent_titles = ParentTitle.objects.filter(serial_number__in=maxus_serials)
            maxus_child_titles = ChildTitle.objects.filter(parent__in=maxus_parent_titles)
            
            # Get parts for these child titles
            parts_to_delete = Part.objects.filter(child_title__in=maxus_child_titles)
            count = parts_to_delete.count()
            
            if self.verbose:
                self.stdout.write(f"🗑️  Removing {count} parts...")
            
            if not self.dry_run:
                deleted_count = parts_to_delete.delete()[0]
                self.stats['parts_deleted'] = deleted_count
                logger.info(f"Deleted {deleted_count} parts")
            else:
                self.stats['parts_deleted'] = count
                
        except Exception as e:
            error_msg = f"Error removing parts: {e}"
            logger.error(error_msg)
            self.stats['errors'] += 1
            if self.verbose:
                self.stdout.write(self.style.ERROR(f"❌ {error_msg}"))

    def _remove_child_titles(self):
        """Remove all Maxus child titles"""
        try:
            # Get Maxus serials
            maxus_serials = SerialNumber.objects.filter(serial__startswith='VM')
            maxus_parent_titles = ParentTitle.objects.filter(serial_number__in=maxus_serials)
            
            # Get child titles for these parent titles
            child_titles_to_delete = ChildTitle.objects.filter(parent__in=maxus_parent_titles)
            count = child_titles_to_delete.count()
            
            if self.verbose:
                self.stdout.write(f"🗑️  Removing {count} child titles...")
            
            if not self.dry_run:
                deleted_count = child_titles_to_delete.delete()[0]
                self.stats['child_titles_deleted'] = deleted_count
                logger.info(f"Deleted {deleted_count} child titles")
            else:
                self.stats['child_titles_deleted'] = count
                
        except Exception as e:
            error_msg = f"Error removing child titles: {e}"
            logger.error(error_msg)
            self.stats['errors'] += 1
            if self.verbose:
                self.stdout.write(self.style.ERROR(f"❌ {error_msg}"))

    def _remove_parent_titles(self):
        """Remove all Maxus parent titles"""
        try:
            # Get Maxus serials
            maxus_serials = SerialNumber.objects.filter(serial__startswith='VM')
            
            # Get parent titles for these serials
            parent_titles_to_delete = ParentTitle.objects.filter(serial_number__in=maxus_serials)
            count = parent_titles_to_delete.count()
            
            if self.verbose:
                self.stdout.write(f"🗑️  Removing {count} parent titles...")
            
            if not self.dry_run:
                deleted_count = parent_titles_to_delete.delete()[0]
                self.stats['parent_titles_deleted'] = deleted_count
                logger.info(f"Deleted {deleted_count} parent titles")
            else:
                self.stats['parent_titles_deleted'] = count
                
        except Exception as e:
            error_msg = f"Error removing parent titles: {e}"
            logger.error(error_msg)
            self.stats['errors'] += 1
            if self.verbose:
                self.stdout.write(self.style.ERROR(f"❌ {error_msg}"))

    def _remove_serial_numbers(self):
        """Remove all Maxus serial numbers"""
        try:
            # Get Maxus serials (VM prefix)
            serials_to_delete = SerialNumber.objects.filter(serial__startswith='VM')
            count = serials_to_delete.count()
            
            if self.verbose:
                self.stdout.write(f"🗑️  Removing {count} serial numbers...")
            
            if not self.dry_run:
                deleted_count = serials_to_delete.delete()[0]
                self.stats['serials_deleted'] = deleted_count
                logger.info(f"Deleted {deleted_count} serial numbers")
            else:
                self.stats['serials_deleted'] = count
                
        except Exception as e:
            error_msg = f"Error removing serial numbers: {e}"
            logger.error(error_msg)
            self.stats['errors'] += 1
            if self.verbose:
                self.stdout.write(self.style.ERROR(f"❌ {error_msg}"))

    def _remove_categories(self):
        """Remove all Maxus categories"""
        try:
            # Get Maxus categories
            categories_to_delete = Category.objects.filter(
                Q(name__icontains='maxus') | Q(slug__icontains='maxus')
            )
            count = categories_to_delete.count()
            
            if self.verbose:
                self.stdout.write(f"🗑️  Removing {count} categories...")
            
            if not self.dry_run:
                deleted_count = categories_to_delete.delete()[0]
                self.stats['categories_deleted'] = deleted_count
                logger.info(f"Deleted {deleted_count} categories")
            else:
                self.stats['categories_deleted'] = count
                
        except Exception as e:
            error_msg = f"Error removing categories: {e}"
            logger.error(error_msg)
            self.stats['errors'] += 1
            if self.verbose:
                self.stdout.write(self.style.ERROR(f"❌ {error_msg}"))

    def _print_final_stats(self):
        """Print final removal statistics"""
        mode = "DRY RUN" if self.dry_run else "ACTUAL DELETION"
        
        self.stdout.write(f"=== Removal Statistics ({mode}) ===")
        self.stdout.write(f"Categories removed: {self.stats['categories_deleted']}")
        self.stdout.write(f"Products removed: {self.stats['products_deleted']}")
        self.stdout.write(f"Stock records removed: {self.stats['stock_records_deleted']}")
        self.stdout.write(f"Parts removed: {self.stats['parts_deleted']}")
        self.stdout.write(f"Child titles removed: {self.stats['child_titles_deleted']}")
        self.stdout.write(f"Parent titles removed: {self.stats['parent_titles_deleted']}")
        self.stdout.write(f"Serial numbers removed: {self.stats['serials_deleted']}")
        self.stdout.write(f"Pricing data removed: {self.stats['pricing_data_deleted']}")
        self.stdout.write(f"Errors encountered: {self.stats['errors']}")
        
        # Log statistics
        logger.info(f"=== FINAL REMOVAL STATISTICS ({mode}) ===")
        logger.info(f"Categories removed: {self.stats['categories_deleted']}")
        logger.info(f"Products removed: {self.stats['products_deleted']}")
        logger.info(f"Stock records removed: {self.stats['stock_records_deleted']}")
        logger.info(f"Parts removed: {self.stats['parts_deleted']}")
        logger.info(f"Child titles removed: {self.stats['child_titles_deleted']}")
        logger.info(f"Parent titles removed: {self.stats['parent_titles_deleted']}")
        logger.info(f"Serial numbers removed: {self.stats['serials_deleted']}")
        logger.info(f"Pricing data removed: {self.stats['pricing_data_deleted']}")
        logger.info(f"Errors encountered: {self.stats['errors']}")
        
        # Total count
        total_removed = (
            self.stats['categories_deleted'] + 
            self.stats['products_deleted'] + 
            self.stats['stock_records_deleted'] + 
            self.stats['parts_deleted'] + 
            self.stats['child_titles_deleted'] + 
            self.stats['parent_titles_deleted'] + 
            self.stats['serials_deleted'] + 
            self.stats['pricing_data_deleted']
        )
        
        if self.dry_run:
            self.stdout.write(self.style.SUCCESS(f"🔍 Would remove {total_removed} total records"))
        else:
            self.stdout.write(self.style.SUCCESS(f"✅ Successfully removed {total_removed} total records"))
        
        # Database verification
        self._verify_database_final()

    def _verify_database_final(self):
        """Final database verification"""
        with connection.cursor() as cursor:
            self.stdout.write("🗄️ FINAL DATABASE VERIFICATION:")
            cursor.execute("SELECT current_database()")
            db_name = cursor.fetchone()[0]
            self.stdout.write(f"   Operations performed on database: {db_name}")
            
            # Check remaining Maxus data
            cursor.execute("SELECT COUNT(*) FROM catalogue_category WHERE name ILIKE '%maxus%' OR slug ILIKE '%maxus%';")
            maxus_cats = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM motorpartsdata_serialnumber WHERE serial LIKE 'VM%';")
            vm_serials = cursor.fetchone()[0]
            
            self.stdout.write(f"   Remaining Maxus categories: {maxus_cats}")
            self.stdout.write(f"   Remaining VM serial numbers: {vm_serials}")
            
            if not self.dry_run:
                if maxus_cats == 0 and vm_serials == 0:
                    self.stdout.write(self.style.SUCCESS("✅ All Maxus data successfully removed"))
                else:
                    self.stdout.write(self.style.WARNING("⚠️ Some Maxus data may still remain"))

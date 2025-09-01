"""
Django management command to clean up incorrectly created categories.

This command removes categories that were created as root categories instead of 
being properly nested under vehicle brands. It preserves the correct vehicle 
brand categories: Maxus, Peugeot, Renault, Mercedes, MAN.

Usage:
    python manage.py cleanup_categories --dry-run  # See what would be deleted
    python manage.py cleanup_categories             # Actually delete categories
    python manage.py cleanup_categories --verbose  # Show detailed output
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from oscar.apps.catalogue.models import Category, Product
from oscar.apps.partner.models import StockRecord
import logging

# Set up logging
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Clean up incorrectly created categories, preserving proper vehicle brands'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dry_run = False
        self.verbose = False
        self.stats = {
            'categories_deleted': 0,
            'products_orphaned': 0,
            'products_reassigned': 0,
            'stock_records_updated': 0
        }
        
        # Define the valid vehicle brand categories that should be preserved
        self.valid_brands = ['Maxus', 'Peugeot', 'Renault', 'Mercedes', 'MAN']

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without making changes'
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
            # Find categories to delete
            categories_to_delete = self._find_categories_to_delete()
            
            if not categories_to_delete:
                self.stdout.write(
                    self.style.SUCCESS("No categories found that need to be deleted!")
                )
                return
            
            # Show what will be deleted
            self._show_deletion_summary(categories_to_delete)
            
            if not self.dry_run:
                # Confirm deletion
                confirm = input("\nAre you sure you want to delete these categories? (yes/no): ")
                if confirm.lower() != 'yes':
                    self.stdout.write("Deletion cancelled.")
                    return
                
                # Perform the cleanup
                self._cleanup_categories(categories_to_delete)
            
            # Show final statistics
            self._print_final_stats()
            
        except Exception as e:
            raise CommandError(f"Cleanup failed: {e}")

    def _find_categories_to_delete(self):
        """Find all categories that should be deleted"""
        # Get all root categories (depth=1)
        root_categories = Category.objects.filter(depth=1)
        
        categories_to_delete = []
        
        for category in root_categories:
            # Keep valid vehicle brand categories
            if category.name in self.valid_brands:
                if self.verbose:
                    self.stdout.write(f"✅ Keeping valid brand: {category.name}")
                continue
            
            # Flag for deletion if it looks like an incorrectly created category
            # These are typically categories with serial numbers or part names
            if self._is_invalid_root_category(category):
                categories_to_delete.append(category)
                if self.verbose:
                    self.stdout.write(f"❌ Marking for deletion: {category.name}")
        
        return categories_to_delete

    def _is_invalid_root_category(self, category):
        """Determine if a root category was incorrectly created"""
        name = category.name
        
        # Check for patterns that indicate incorrectly created categories
        invalid_patterns = [
            # Categories with serial numbers (LSH, WJZ, etc.)
            'LSH' in name,
            'WJZ' in name,
            'VF1' in name,
            'VF3' in name,
            'WDF' in name,
            'WDB' in name,
            'WMA' in name,
            'LDV' in name,
            'MX' in name,
            # Categories with part numbers (C00, B00, etc.)
            'C00' in name,
            'B00' in name,
            'JE' in name and 'A00' in name,
            'FE' in name and 'A00' in name,
            # Categories with dashes indicating concatenated names
            ' - ' in name,
            # Very long category names (likely concatenated)
            len(name) > 50,
        ]
        
        return any(invalid_patterns)

    def _show_deletion_summary(self, categories_to_delete):
        """Show summary of what will be deleted"""
        self.stdout.write(f"\n🗑️  Found {len(categories_to_delete)} categories to delete:")
        self.stdout.write("=" * 60)
        
        total_children = 0
        total_products = 0
        
        for category in categories_to_delete:
            # Count children recursively
            children_count = category.get_descendant_count()
            total_children += children_count
            
            # Count products in this category and its children
            category_descendants = list(category.get_descendants()) + [category]
            products_count = Product.objects.filter(categories__in=category_descendants).count()
            total_products += products_count
            
            self.stdout.write(f"📁 {category.name} (ID: {category.id})")
            if children_count > 0:
                self.stdout.write(f"   └── {children_count} child categories")
            if products_count > 0:
                self.stdout.write(f"   └── {products_count} products")
            self.stdout.write("")
        
        self.stdout.write("=" * 60)
        self.stdout.write(f"📊 SUMMARY:")
        self.stdout.write(f"   Categories to delete: {len(categories_to_delete)}")
        self.stdout.write(f"   Child categories: {total_children}")
        self.stdout.write(f"   Products affected: {total_products}")
        self.stdout.write("=" * 60)

    def _cleanup_categories(self, categories_to_delete):
        """Actually delete the categories and handle orphaned products"""
        self.stdout.write("🧹 Starting cleanup...")
        
        with transaction.atomic():
            for category in categories_to_delete:
                # Get all products in this category tree before deletion
                category_descendants = list(category.get_descendants()) + [category]
                products_in_category = Product.objects.filter(
                    categories__in=category_descendants
                ).distinct()
                
                # Handle products that will become orphaned
                for product in products_in_category:
                    self._handle_orphaned_product(product, category)
                
                # Count children before deletion
                children_count = category.get_descendant_count()
                
                if self.verbose:
                    self.stdout.write(f"Deleting category: {category.name} and {children_count} children")
                
                # Delete the category (this will cascade to children)
                category.delete()
                
                self.stats['categories_deleted'] += 1 + children_count

    def _handle_orphaned_product(self, product, deleted_category):
        """Handle products that will lose their category"""
        # Try to find a valid vehicle brand category to reassign to
        valid_category = self._find_appropriate_category_for_product(product)
        
        if valid_category:
            # Remove from deleted category and add to valid category
            product.categories.remove(deleted_category)
            product.categories.add(valid_category)
            self.stats['products_reassigned'] += 1
            
            if self.verbose:
                self.stdout.write(f"   📦 Reassigned product {product.title} to {valid_category.name}")
        else:
            # Product will become orphaned
            self.stats['products_orphaned'] += 1
            
            if self.verbose:
                self.stdout.write(f"   ⚠️  Product {product.title} will become orphaned")

    def _find_appropriate_category_for_product(self, product):
        """Find an appropriate category for an orphaned product"""
        # Try to determine vehicle brand from product title or UPC
        product_info = f"{product.title} {product.upc or ''}".upper()
        
        # Check for vehicle brand indicators
        for brand in self.valid_brands:
            brand_category = Category.objects.filter(name=brand, depth=1).first()
            if brand_category:
                # Simple heuristic: if product contains brand-related keywords
                if brand.upper() in product_info:
                    return brand_category
                
                # Check for serial number patterns
                if brand == 'Maxus' and any(pattern in product_info for pattern in ['LSH', 'LDV', 'MX']):
                    return brand_category
                elif brand == 'Peugeot' and any(pattern in product_info for pattern in ['WJZ', 'VF3', 'PG']):
                    return brand_category
                elif brand == 'Renault' and any(pattern in product_info for pattern in ['VF1', 'RN', 'RE']):
                    return brand_category
                elif brand == 'Mercedes' and any(pattern in product_info for pattern in ['WDF', 'WDB', 'MB']):
                    return brand_category
                elif brand == 'MAN' and any(pattern in product_info for pattern in ['WMA', 'MN']):
                    return brand_category
        
        # Default to Maxus if no specific brand can be determined
        return Category.objects.filter(name='Maxus', depth=1).first()

    def _print_final_stats(self):
        """Print final cleanup statistics"""
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("📊 CLEANUP COMPLETED")
        self.stdout.write("=" * 60)
        self.stdout.write(f"Categories deleted: {self.stats['categories_deleted']}")
        self.stdout.write(f"Products reassigned: {self.stats['products_reassigned']}")
        self.stdout.write(f"Products orphaned: {self.stats['products_orphaned']}")
        self.stdout.write("=" * 60)
        
        if not self.dry_run:
            self.stdout.write(
                self.style.SUCCESS("✅ Cleanup completed successfully!")
            )
        else:
            self.stdout.write(
                self.style.WARNING("ℹ️  This was a dry run - no changes were made")
            )

#!/usr/bin/env python
"""
Management command to list products that have had their prices updated from Excel sheets.
Shows which products have the price_updated flag set to True.

Usage: python manage.py list_price_updates [--reset-flags] [--show-details]
"""

from django.core.management.base import BaseCommand
from django.db.models import Q
from oscar.apps.partner.models import StockRecord
from oscar.apps.catalogue.models import Product


class Command(BaseCommand):
    help = 'List products that have had their prices updated from Excel imports'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset-flags',
            action='store_true',
            help='Reset the price_updated flags for all products after showing them'
        )
        parser.add_argument(
            '--show-details',
            action='store_true',
            help='Show detailed information including update dates and notes'
        )
        parser.add_argument(
            '--updated-only',
            action='store_true',
            help='Show only products that have been updated (default shows all)'
        )

    def handle(self, *args, **options):
        reset_flags = options['reset_flags']
        show_details = options['show_details']
        updated_only = options['updated_only']

        # Get stock records with price updates
        if updated_only:
            stock_records = StockRecord.objects.filter(price_updated=True).select_related('product')
        else:
            stock_records = StockRecord.objects.all().select_related('product')

        # Count totals
        total_records = stock_records.count()
        updated_count = stock_records.filter(price_updated=True).count()

        if total_records == 0:
            self.stdout.write(self.style.WARNING("No stock records found"))
            return

        self.stdout.write("="*80)
        self.stdout.write("PRICE UPDATE STATUS")
        self.stdout.write("="*80)
        self.stdout.write(f"Total stock records: {total_records}")
        self.stdout.write(f"Records with price updates: {updated_count}")
        self.stdout.write(f"Records without updates: {total_records - updated_count}")
        self.stdout.write("")

        if updated_count == 0:
            self.stdout.write(self.style.WARNING("No products have been marked as price updated"))
            return

        # Display records
        self.stdout.write("PRODUCTS WITH PRICE UPDATES:")
        self.stdout.write("-" * 80)

        for record in stock_records.filter(price_updated=True):
            product = record.product
            sku = product.upc or "No SKU"
            price = f"£{record.price}" if record.price else "No price"
            
            # Basic info line
            status_icon = "✓" if record.price_updated else "✗"
            self.stdout.write(f"{status_icon} {product.title[:50]:<50} SKU: {sku:<15} Price: {price}")
            
            # Detailed info if requested
            if show_details:
                if record.price_update_date:
                    self.stdout.write(f"    Updated: {record.price_update_date.strftime('%Y-%m-%d %H:%M:%S')}")
                if record.price_update_notes:
                    # Truncate long notes
                    notes = record.price_update_notes[:100] + "..." if len(record.price_update_notes) > 100 else record.price_update_notes
                    self.stdout.write(f"    Notes: {notes}")
                self.stdout.write("")

        # Reset flags if requested
        if reset_flags:
            self.stdout.write("\n" + "-" * 50)
            if input("Reset all price_updated flags? (y/N): ").lower() == 'y':
                reset_count = 0
                for record in stock_records.filter(price_updated=True):
                    record.reset_price_update_flag()
                    reset_count += 1
                
                self.stdout.write(self.style.SUCCESS(f"Reset {reset_count} price update flags"))
            else:
                self.stdout.write("Reset cancelled")

        # Show commands for next steps
        self.stdout.write("\n" + "="*50)
        self.stdout.write("USEFUL COMMANDS:")
        self.stdout.write("="*50)
        self.stdout.write("Update prices from Excel:")
        self.stdout.write("  python manage.py update_prices_from_excel /path/to/file.xlsx --dry-run")
        self.stdout.write("")
        self.stdout.write("Reset all price update flags:")
        self.stdout.write("  python manage.py list_price_updates --reset-flags")
        self.stdout.write("")
        self.stdout.write("Show detailed update information:")
        self.stdout.write("  python manage.py list_price_updates --show-details")

#!/usr/bin/env python
"""
Management command to list products that have had their prices updated from Excel sheets.
Shows tracking records from the PriceUpdateTracker model.

Usage: python manage.py list_price_updates [--reset-flags] [--show-details]
"""

from django.core.management.base import BaseCommand
from django.db.models import Q
from motorpartsdata.models import PriceUpdateTracker
from oscar.apps.catalogue.models import Product


class Command(BaseCommand):
    help = 'List products that have had their prices updated from Excel imports'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset-flags',
            action='store_true',
            help='Reset the price_updated flags for all tracking records after showing them'
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
        parser.add_argument(
            '--excel-file',
            type=str,
            help='Filter by specific Excel filename'
        )

    def handle(self, *args, **options):
        reset_flags = options['reset_flags']
        show_details = options['show_details']
        updated_only = options['updated_only']
        excel_file = options['excel_file']

        # Get tracking records
        tracking_records = PriceUpdateTracker.objects.all()

        # Apply filters
        if updated_only:
            tracking_records = tracking_records.filter(price_updated=True)
        
        if excel_file:
            tracking_records = tracking_records.filter(excel_filename__icontains=excel_file)

        # Count totals
        total_records = tracking_records.count()
        updated_count = tracking_records.filter(price_updated=True).count()

        if total_records == 0:
            if excel_file:
                self.stdout.write(self.style.WARNING(f"No price update records found for Excel file: {excel_file}"))
            else:
                self.stdout.write(self.style.WARNING("No price update records found"))
            return

        self.stdout.write("="*80)
        self.stdout.write("PRICE UPDATE TRACKING RECORDS")
        self.stdout.write("="*80)
        self.stdout.write(f"Total tracking records: {total_records}")
        self.stdout.write(f"Records marked as updated: {updated_count}")
        self.stdout.write(f"Records marked as processed: {total_records - updated_count}")
        self.stdout.write("")

        if updated_count == 0 and updated_only:
            self.stdout.write(self.style.WARNING("No products are currently marked as updated"))
            return

        # Display records
        self.stdout.write("PRICE UPDATE TRACKING RECORDS:")
        self.stdout.write("-" * 80)

        # Display with proper formatting
        for record in tracking_records.order_by('-update_date'):
            status_icon = "✓" if record.price_updated else "✗"
            
            # Try to get product title
            try:
                product = Product.objects.get(upc=record.product_sku)
                product_name = product.title[:40] + "..." if len(product.title) > 40 else product.title
            except Product.DoesNotExist:
                product_name = "Product not found"
            except Product.MultipleObjectsReturned:
                product_name = "Multiple products found"
            
            # Basic info line
            price_change = ""
            if record.old_price:
                price_change = f"£{record.old_price} → £{record.new_price}"
            else:
                price_change = f"New: £{record.new_price}"
            
            self.stdout.write(
                f"{status_icon} SKU: {record.product_sku:<15} {product_name:<45} {price_change}"
            )
            
            # Detailed info if requested
            if show_details:
                self.stdout.write(f"    Updated: {record.update_date.strftime('%Y-%m-%d %H:%M:%S')}")
                self.stdout.write(f"    Excel file: {record.excel_filename}")
                if record.updated_by:
                    self.stdout.write(f"    Updated by: {record.updated_by}")
                if record.notes:
                    # Truncate long notes
                    notes = record.notes[:80] + "..." if len(record.notes) > 80 else record.notes
                    self.stdout.write(f"    Notes: {notes}")
                self.stdout.write("")

        # Show summary by Excel file
        if not excel_file:
            self.stdout.write("\n" + "-" * 50)
            self.stdout.write("SUMMARY BY EXCEL FILE:")
            self.stdout.write("-" * 50)
            
            # Group by Excel filename
            excel_files = tracking_records.values_list('excel_filename', flat=True).distinct()
            for filename in excel_files:
                file_records = tracking_records.filter(excel_filename=filename)
                file_updated = file_records.filter(price_updated=True).count()
                file_total = file_records.count()
                self.stdout.write(f"{filename}: {file_updated}/{file_total} records updated")

        # Reset flags if requested
        if reset_flags:
            self.stdout.write("\n" + "-" * 50)
            if input("Reset all price_updated flags? (y/N): ").lower() == 'y':
                reset_count = PriceUpdateTracker.reset_all_flags()
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
        self.stdout.write("")
        self.stdout.write("Filter by Excel file:")
        self.stdout.write("  python manage.py list_price_updates --excel-file filename.xlsx")

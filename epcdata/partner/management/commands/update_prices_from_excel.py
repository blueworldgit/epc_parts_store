#!/usr/bin/env python
"""
Management command to update prices from Excel sheet using SKU matching.
This command reads an Excel file, matches products by SKU, updates prices,
and tracks which products have been updated.

Usage: python manage.py update_prices_from_excel /path/to/excel_file.xlsx [--dry-run] [--verbose]
"""

import os
import pandas as pd
from decimal import Decimal, InvalidOperation
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from oscar.apps.partner.models import StockRecord
from oscar.apps.catalogue.models import Product


class Command(BaseCommand):
    help = 'Update product prices from Excel file using SKU matching'

    def add_arguments(self, parser):
        parser.add_argument(
            'excel_file',
            type=str,
            help='Path to the Excel file containing SKU and price data'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output'
        )
        parser.add_argument(
            '--sku-column',
            type=str,
            default='SKU',
            help='Name of the SKU column in Excel (default: SKU)'
        )
        parser.add_argument(
            '--price-column',
            type=str,
            default='Price',
            help='Name of the price column in Excel (default: Price)'
        )
        parser.add_argument(
            '--sheet-name',
            type=str,
            default=0,
            help='Excel sheet name or index (default: first sheet)'
        )

    def handle(self, *args, **options):
        excel_file = options['excel_file']
        dry_run = options['dry_run']
        verbose = options['verbose']
        sku_column = options['sku_column']
        price_column = options['price_column']
        sheet_name = options['sheet_name']

        # Check if file exists
        if not os.path.exists(excel_file):
            raise CommandError(f'Excel file not found: {excel_file}')

        # Statistics tracking
        stats = {
            'total_rows': 0,
            'skus_processed': 0,
            'prices_updated': 0,
            'products_not_found': 0,
            'invalid_prices': 0,
            'errors': 0
        }

        try:
            # Read Excel file
            if verbose:
                self.stdout.write(f"Reading Excel file: {excel_file}")
            
            df = pd.read_excel(excel_file, sheet_name=sheet_name)
            stats['total_rows'] = len(df)
            
            if verbose:
                self.stdout.write(f"Found {stats['total_rows']} rows in Excel file")
                self.stdout.write(f"Looking for columns: {sku_column}, {price_column}")

            # Check if required columns exist
            if sku_column not in df.columns:
                raise CommandError(f'SKU column "{sku_column}" not found in Excel file. Available columns: {list(df.columns)}')
            
            if price_column not in df.columns:
                raise CommandError(f'Price column "{price_column}" not found in Excel file. Available columns: {list(df.columns)}')

            # Process each row
            with transaction.atomic():
                for index, row in df.iterrows():
                    try:
                        sku = str(row[sku_column]).strip()
                        price_value = row[price_column]
                        
                        if pd.isna(price_value) or sku == 'nan' or not sku:
                            if verbose:
                                self.stdout.write(f"Row {index + 1}: Skipping empty SKU or price")
                            continue
                        
                        stats['skus_processed'] += 1
                        
                        # Convert price to Decimal
                        try:
                            # Handle various price formats
                            if isinstance(price_value, str):
                                # Remove currency symbols and whitespace
                                price_str = price_value.replace('£', '').replace('$', '').replace(',', '').strip()
                                price = Decimal(price_str)
                            else:
                                price = Decimal(str(price_value))
                            
                            if price < 0:
                                raise ValueError("Negative price")
                                
                        except (InvalidOperation, ValueError, TypeError) as e:
                            if verbose:
                                self.stdout.write(f"Row {index + 1}: Invalid price '{price_value}' for SKU '{sku}': {e}")
                            stats['invalid_prices'] += 1
                            continue
                        
                        # Find product by SKU (UPC in Oscar)
                        try:
                            product = Product.objects.get(upc=sku)
                        except Product.DoesNotExist:
                            if verbose:
                                self.stdout.write(f"Row {index + 1}: Product not found for SKU '{sku}'")
                            stats['products_not_found'] += 1
                            continue
                        except Product.MultipleObjectsReturned:
                            if verbose:
                                self.stdout.write(f"Row {index + 1}: Multiple products found for SKU '{sku}', using first one")
                            product = Product.objects.filter(upc=sku).first()
                        
                        # Find stock record for this product
                        stock_record = StockRecord.objects.filter(product=product).first()
                        
                        if not stock_record:
                            if verbose:
                                self.stdout.write(f"Row {index + 1}: No stock record found for product '{product.title}' (SKU: {sku})")
                            stats['products_not_found'] += 1
                            continue
                        
                        # Check if price has changed
                        old_price = stock_record.price
                        if old_price == price:
                            if verbose:
                                self.stdout.write(f"Row {index + 1}: Price unchanged for '{product.title}' (SKU: {sku}) - £{price}")
                            continue
                        
                        # Update price and tracking fields
                        if not dry_run:
                            stock_record.price = price
                            notes = f"Updated from Excel file: {os.path.basename(excel_file)} on {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}"
                            if old_price:
                                notes += f" (Previous price: £{old_price})"
                            stock_record.mark_price_updated(notes)
                        
                        stats['prices_updated'] += 1
                        
                        if verbose:
                            action = "Would update" if dry_run else "Updated"
                            self.stdout.write(
                                f"Row {index + 1}: {action} '{product.title}' (SKU: {sku}) "
                                f"from £{old_price or 'None'} to £{price}"
                            )
                        
                    except Exception as e:
                        stats['errors'] += 1
                        self.stdout.write(
                            self.style.ERROR(f"Row {index + 1}: Error processing SKU '{sku}': {str(e)}")
                        )
                        continue

                # If dry run, rollback the transaction
                if dry_run:
                    transaction.set_rollback(True)
                    self.stdout.write(self.style.WARNING("DRY RUN: No changes were made to the database"))

        except Exception as e:
            raise CommandError(f'Error reading Excel file: {str(e)}')

        # Print statistics
        self.stdout.write("\n" + "="*50)
        self.stdout.write("PRICE UPDATE SUMMARY")
        self.stdout.write("="*50)
        self.stdout.write(f"Excel file: {excel_file}")
        self.stdout.write(f"Total rows in Excel: {stats['total_rows']}")
        self.stdout.write(f"SKUs processed: {stats['skus_processed']}")
        self.stdout.write(f"Prices updated: {stats['prices_updated']}")
        self.stdout.write(f"Products not found: {stats['products_not_found']}")
        self.stdout.write(f"Invalid prices: {stats['invalid_prices']}")
        self.stdout.write(f"Errors: {stats['errors']}")
        
        if dry_run:
            self.stdout.write(self.style.WARNING("\nThis was a DRY RUN - no changes were made"))
            self.stdout.write("Remove --dry-run flag to apply changes")
        else:
            self.stdout.write(self.style.SUCCESS(f"\nSuccessfully updated {stats['prices_updated']} prices"))
        
        # Show how to check updated products
        if stats['prices_updated'] > 0 and not dry_run:
            self.stdout.write("\nTo see products with updated prices, run:")
            self.stdout.write("python manage.py list_price_updates")

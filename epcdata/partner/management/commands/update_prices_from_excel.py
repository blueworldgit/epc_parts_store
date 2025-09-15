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
            '--report-file',
            type=str,
            help='Output file for detailed report (default: price_update_report_TIMESTAMP.txt)'
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
        report_file = options.get('report_file')

        # Generate report filename if not provided
        if not report_file:
            timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
            report_file = f'price_update_report_{timestamp}.txt'
        
        # Initialize report content
        report_lines = []
        report_lines.append("="*80)
        report_lines.append("PRICE UPDATE DETAILED REPORT")
        report_lines.append("="*80)
        report_lines.append(f"Generated: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"Excel file: {excel_file}")
        report_lines.append(f"SKU column: {sku_column}")
        report_lines.append(f"Price column: {price_column}")
        report_lines.append(f"Dry run: {dry_run}")
        report_lines.append("="*80)
        report_lines.append("")

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
            'errors': 0,
            'multiple_products_found': 0,
            'products_updated': 0
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
                            products = [product]  # Single product found
                        except Product.DoesNotExist:
                            if verbose:
                                self.stdout.write(f"Row {index + 1}: Product not found for SKU '{sku}'")
                            report_lines.append(f"Row {index + 1}: ❌ Product not found for SKU '{sku}'")
                            stats['products_not_found'] += 1
                            continue
                        except Product.MultipleObjectsReturned:
                            # Handle multiple products with same SKU
                            products = Product.objects.filter(upc=sku)
                            stats['multiple_products_found'] += 1
                            if verbose:
                                self.stdout.write(f"Row {index + 1}: Found {products.count()} products for SKU '{sku}', updating all")
                            report_lines.append(f"Row {index + 1}: 🔄 Found {products.count()} products for SKU '{sku}', updating all:")
                        
                        # Process each product found
                        products_updated_for_sku = 0
                        for product in products:
                            try:
                                # Find stock record for this product
                                stock_record = StockRecord.objects.filter(product=product).first()
                                
                                if not stock_record:
                                    if verbose:
                                        self.stdout.write(f"  Product '{product.title}' (ID: {product.id}) - No stock record")
                                    report_lines.append(f"    ⚠️  Product '{product.title}' (ID: {product.id}) - No stock record")
                                    continue
                                
                                # Check if price has changed
                                old_price = stock_record.price
                                if old_price == price:
                                    if verbose:
                                        self.stdout.write(f"  Product '{product.title}' (ID: {product.id}) - Price unchanged: £{price}")
                                    report_lines.append(f"    ➡️  Product '{product.title}' (ID: {product.id}) - Price unchanged: £{price}")
                                    continue
                                
                                # Update price and tracking fields
                                if not dry_run:
                                    stock_record.price = price
                                    notes = f"Updated from Excel file: {os.path.basename(excel_file)} on {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}"
                                    if old_price:
                                        notes += f" (Previous price: £{old_price})"
                                    stock_record.mark_price_updated(notes)
                                
                                stats['prices_updated'] += 1
                                products_updated_for_sku += 1
                                
                                action = "Would update" if dry_run else "Updated"
                                update_msg = f"  {action} '{product.title}' (ID: {product.id}) from £{old_price or 'None'} to £{price}"
                                
                                if verbose:
                                    self.stdout.write(update_msg)
                                report_lines.append(f"    ✅ {update_msg}")
                                
                            except Exception as product_error:
                                error_msg = f"  Error updating product '{product.title}' (ID: {product.id}): {str(product_error)}"
                                self.stdout.write(self.style.ERROR(error_msg))
                                report_lines.append(f"    ❌ {error_msg}")
                        
                        if products_updated_for_sku > 0:
                            stats['products_updated'] += products_updated_for_sku
                        
                    except Exception as e:
                        stats['errors'] += 1
                        error_msg = f"Row {index + 1}: Error processing SKU '{sku}': {str(e)}"
                        self.stdout.write(self.style.ERROR(error_msg))
                        report_lines.append(f"Row {index + 1}: ❌ {error_msg}")
                        continue

                # If dry run, rollback the transaction
                if dry_run:
                    transaction.set_rollback(True)
                    self.stdout.write(self.style.WARNING("DRY RUN: No changes were made to the database"))

        except Exception as e:
            raise CommandError(f'Error reading Excel file: {str(e)}')

        # Add summary to report
        report_lines.append("")
        report_lines.append("="*80)
        report_lines.append("SUMMARY STATISTICS")
        report_lines.append("="*80)
        report_lines.append(f"Excel file: {excel_file}")
        report_lines.append(f"Total rows in Excel: {stats['total_rows']}")
        report_lines.append(f"SKUs processed: {stats['skus_processed']}")
        report_lines.append(f"Individual products updated: {stats['prices_updated']}")
        report_lines.append(f"Unique SKUs with updates: {stats['products_updated']}")
        report_lines.append(f"SKUs with multiple products: {stats['multiple_products_found']}")
        report_lines.append(f"Products not found: {stats['products_not_found']}")
        report_lines.append(f"Invalid prices: {stats['invalid_prices']}")
        report_lines.append(f"Errors: {stats['errors']}")
        
        if dry_run:
            report_lines.append("")
            report_lines.append("⚠️  THIS WAS A DRY RUN - NO CHANGES WERE MADE")
        else:
            report_lines.append("")
            report_lines.append(f"✅ Successfully updated {stats['prices_updated']} prices across {stats['products_updated']} products")

        # Write report to file
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(report_lines))
            self.stdout.write(f"\n📄 Detailed report saved to: {report_file}")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error writing report file: {str(e)}"))

        # Print statistics to console
        self.stdout.write("\n" + "="*50)
        self.stdout.write("PRICE UPDATE SUMMARY")
        self.stdout.write("="*50)
        self.stdout.write(f"Excel file: {excel_file}")
        self.stdout.write(f"Total rows in Excel: {stats['total_rows']}")
        self.stdout.write(f"SKUs processed: {stats['skus_processed']}")
        self.stdout.write(f"Individual products updated: {stats['prices_updated']}")
        self.stdout.write(f"SKUs with multiple products: {stats['multiple_products_found']}")
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

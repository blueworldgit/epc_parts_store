"""
Enhanced Django management command to update prices from Excel sheet using SKU matching.
This version includes comprehensive debugging and error handling.

Usage: python manage.py update_prices_from_excel_debug /path/to/excel_file.xlsx [--dry-run] [--verbose]
"""

import os
import pandas as pd
from decimal import Decimal, InvalidOperation
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.db import transaction

from oscar.apps.catalogue.models import Product
from oscar.apps.partner.models import StockRecord


class Command(BaseCommand):
    help = 'Update product prices from Excel file using SKU matching (DEBUG VERSION)'

    def add_arguments(self, parser):
        parser.add_argument(
            'excel_file',
            type=str,
            help='Path to the Excel file containing SKU and price data'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without making actual changes'
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

    def handle(self, *args, **options):
        excel_file = options['excel_file']
        dry_run = options['dry_run']
        verbose = options['verbose']
        sku_column = options['sku_column']
        price_column = options['price_column']
        report_file = options.get('report_file')

        # Generate report filename if not provided
        if not report_file:
            timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
            report_file = f'price_update_debug_report_{timestamp}.txt'
        
        # Initialize report content
        report_lines = []
        report_lines.append("="*80)
        report_lines.append("ENHANCED PRICE UPDATE DEBUG REPORT")
        report_lines.append("="*80)
        report_lines.append(f"Generated: {timezone.now()}")
        report_lines.append(f"Excel file: {excel_file}")
        report_lines.append(f"SKU column: {sku_column}")
        report_lines.append(f"Price column: {price_column}")
        report_lines.append(f"Dry run mode: {dry_run}")
        report_lines.append(f"Verbose mode: {verbose}")
        report_lines.append("")

        # Enhanced statistics tracking
        stats = {
            'total_rows': 0,
            'skus_processed': 0,
            'prices_updated': 0,
            'products_updated': 0,
            'multiple_products_found': 0,
            'products_not_found': 0,
            'invalid_prices': 0,
            'no_stock_records': 0,
            'price_unchanged': 0,
            'database_errors': 0,
            'validation_errors': 0,
            'save_errors': 0,
            'errors': 0,
        }

        self.stdout.write("="*80)
        self.stdout.write("ENHANCED PRICE UPDATE (DEBUG VERSION)")
        self.stdout.write("="*80)
        self.stdout.write(f"Excel file: {excel_file}")
        self.stdout.write(f"Dry run: {dry_run}")
        self.stdout.write("")

        try:
            # Read Excel file with enhanced error handling
            try:
                df = pd.read_excel(excel_file)
                self.stdout.write(f"✅ Successfully loaded Excel file with {len(df)} rows")
                report_lines.append(f"✅ Excel file loaded: {len(df)} rows")
            except Exception as e:
                error_msg = f"❌ Failed to read Excel file: {str(e)}"
                self.stdout.write(self.style.ERROR(error_msg))
                report_lines.append(error_msg)
                raise CommandError(error_msg)

            # Validate columns
            if sku_column not in df.columns:
                error_msg = f"❌ SKU column '{sku_column}' not found. Available columns: {list(df.columns)}"
                self.stdout.write(self.style.ERROR(error_msg))
                report_lines.append(error_msg)
                raise CommandError(error_msg)

            if price_column not in df.columns:
                error_msg = f"❌ Price column '{price_column}' not found. Available columns: {list(df.columns)}"
                self.stdout.write(self.style.ERROR(error_msg))
                report_lines.append(error_msg)
                raise CommandError(error_msg)

            self.stdout.write(f"✅ Found required columns: {sku_column}, {price_column}")
            report_lines.append(f"✅ Columns validated: {sku_column}, {price_column}")
            report_lines.append(f"Available columns: {list(df.columns)}")
            
            # Remove rows with missing SKU or Price
            original_count = len(df)
            df = df.dropna(subset=[sku_column, price_column])
            if len(df) < original_count:
                dropped = original_count - len(df)
                self.stdout.write(f"⚠️  Dropped {dropped} rows with missing SKU or Price")
                report_lines.append(f"⚠️  Dropped {dropped} rows with missing data")

            stats['total_rows'] = len(df)

            # Start database transaction with enhanced debugging
            with transaction.atomic():
                self.stdout.write(f"🔄 Processing {len(df)} rows...")
                report_lines.append("")
                report_lines.append("="*60)
                report_lines.append("DETAILED PROCESSING LOG")
                report_lines.append("="*60)

                for index, row in df.iterrows():
                    try:
                        # Extract and validate data
                        sku = str(row[sku_column]).strip()
                        if not sku or sku.lower() == 'nan':
                            self.stdout.write(f"Row {index + 1}: ⚠️  Empty SKU, skipping")
                            report_lines.append(f"Row {index + 1}: ⚠️  Empty SKU")
                            continue

                        # Enhanced price validation
                        price_raw = row[price_column]
                        self.stdout.write(f"\n📋 Row {index + 1}: Processing SKU '{sku}', Raw price: '{price_raw}' (type: {type(price_raw)})")
                        report_lines.append(f"\nRow {index + 1}: SKU '{sku}', Raw price: '{price_raw}'")

                        try:
                            if pd.isna(price_raw):
                                raise ValueError("Price is NaN")
                            price = Decimal(str(price_raw))
                            if price < 0:
                                raise ValueError(f"Negative price: {price}")
                            self.stdout.write(f"✅ Price validation passed: £{price}")
                            report_lines.append(f"  ✅ Price validated: £{price}")
                        except (ValueError, InvalidOperation) as e:
                            stats['invalid_prices'] += 1
                            error_msg = f"  ❌ Invalid price '{price_raw}': {str(e)}"
                            self.stdout.write(self.style.ERROR(error_msg))
                            report_lines.append(error_msg)
                            continue

                        stats['skus_processed'] += 1

                        # Enhanced product lookup with detailed logging
                        self.stdout.write(f"🔍 Searching for products with SKU '{sku}'...")
                        
                        try:
                            products = Product.objects.filter(upc=sku)
                            product_count = products.count()
                            
                            if product_count == 0:
                                stats['products_not_found'] += 1
                                error_msg = f"  ❌ No products found for SKU '{sku}'"
                                self.stdout.write(self.style.WARNING(error_msg))
                                report_lines.append(error_msg)
                                continue
                            elif product_count > 1:
                                stats['multiple_products_found'] += 1
                                self.stdout.write(f"  🔄 Found {product_count} products for SKU '{sku}'")
                                report_lines.append(f"  🔄 Multiple products found: {product_count}")
                            else:
                                self.stdout.write(f"  ✅ Found 1 product for SKU '{sku}'")
                                report_lines.append(f"  ✅ Single product found")

                        except Exception as db_error:
                            stats['database_errors'] += 1
                            error_msg = f"  ❌ Database error searching for SKU '{sku}': {str(db_error)}"
                            self.stdout.write(self.style.ERROR(error_msg))
                            report_lines.append(error_msg)
                            continue

                        # Process each product with enhanced debugging
                        products_updated_for_sku = 0
                        for i, product in enumerate(products, 1):
                            self.stdout.write(f"    🔧 Processing product {i}/{product_count}: '{product.title}' (ID: {product.id})")
                            report_lines.append(f"    Product {i}: '{product.title}' (ID: {product.id})")
                            
                            try:
                                # Find stock record with enhanced logging
                                stock_records = StockRecord.objects.filter(product=product)
                                stock_count = stock_records.count()
                                
                                if stock_count == 0:
                                    stats['no_stock_records'] += 1
                                    error_msg = f"      ❌ No stock records found"
                                    self.stdout.write(self.style.WARNING(error_msg))
                                    report_lines.append(error_msg)
                                    continue
                                elif stock_count > 1:
                                    self.stdout.write(f"      ⚠️  Multiple stock records ({stock_count}), using first")
                                    report_lines.append(f"      ⚠️  Multiple stock records: {stock_count}")
                                
                                stock_record = stock_records.first()
                                self.stdout.write(f"      📊 Stock record ID: {stock_record.id}, Partner: {stock_record.partner}")
                                report_lines.append(f"      Stock record: ID {stock_record.id}, Partner: {stock_record.partner}")

                                # Enhanced price comparison
                                old_price = stock_record.price
                                self.stdout.write(f"      🔍 Current price: £{old_price}, New price: £{price}")
                                report_lines.append(f"      Price comparison: £{old_price} → £{price}")
                                
                                if old_price == price:
                                    stats['price_unchanged'] += 1
                                    msg = f"      ➡️  Price unchanged: £{price}"
                                    self.stdout.write(msg)
                                    report_lines.append(msg)
                                    continue

                                # Perform the update with enhanced error handling
                                if not dry_run:
                                    try:
                                        self.stdout.write(f"      💾 Updating price in database...")
                                        stock_record.price = price
                                        
                                        # Enhanced save operation with validation
                                        stock_record.full_clean()  # Validate before saving
                                        stock_record.save()
                                        
                                        # Verify the save worked
                                        stock_record.refresh_from_db()
                                        saved_price = stock_record.price
                                        
                                        if saved_price != price:
                                            raise ValueError(f"Save verification failed: expected £{price}, got £{saved_price}")
                                        
                                        self.stdout.write(f"      ✅ Price saved and verified: £{saved_price}")
                                        report_lines.append(f"      ✅ Price updated and verified: £{old_price} → £{saved_price}")
                                        
                                    except Exception as save_error:
                                        stats['save_errors'] += 1
                                        error_msg = f"      ❌ Save error: {str(save_error)}"
                                        self.stdout.write(self.style.ERROR(error_msg))
                                        report_lines.append(error_msg)
                                        continue
                                else:
                                    self.stdout.write(f"      🎭 DRY RUN: Would update £{old_price} → £{price}")
                                    report_lines.append(f"      🎭 DRY RUN: Would update £{old_price} → £{price}")

                                stats['prices_updated'] += 1
                                products_updated_for_sku += 1
                                
                            except Exception as product_error:
                                stats['validation_errors'] += 1
                                error_msg = f"      ❌ Product processing error: {str(product_error)}"
                                self.stdout.write(self.style.ERROR(error_msg))
                                report_lines.append(error_msg)
                                continue

                        if products_updated_for_sku > 0:
                            stats['products_updated'] += 1
                            self.stdout.write(f"  🎯 SKU '{sku}': Updated {products_updated_for_sku} product(s)")
                        
                    except Exception as row_error:
                        stats['errors'] += 1
                        error_msg = f"Row {index + 1}: ❌ Unexpected error: {str(row_error)}"
                        self.stdout.write(self.style.ERROR(error_msg))
                        report_lines.append(error_msg)
                        import traceback
                        traceback_info = traceback.format_exc()
                        self.stdout.write(traceback_info)
                        report_lines.append(f"  Traceback: {traceback_info}")
                        continue

                # Transaction handling
                if dry_run:
                    transaction.set_rollback(True)
                    self.stdout.write(self.style.WARNING("\n🎭 DRY RUN: Rolling back all changes"))
                    report_lines.append("\n🎭 DRY RUN: All changes rolled back")
                else:
                    self.stdout.write(self.style.SUCCESS("\n💾 Committing changes to database"))
                    report_lines.append("\n💾 Changes committed to database")

        except Exception as e:
            error_msg = f'❌ Fatal error: {str(e)}'
            self.stdout.write(self.style.ERROR(error_msg))
            report_lines.append(error_msg)
            raise CommandError(error_msg)

        # Enhanced summary reporting
        report_lines.append("")
        report_lines.append("="*80)
        report_lines.append("ENHANCED SUMMARY STATISTICS")
        report_lines.append("="*80)
        for key, value in stats.items():
            report_lines.append(f"{key.replace('_', ' ').title()}: {value}")
        
        if dry_run:
            report_lines.append("")
            report_lines.append("⚠️  THIS WAS A DRY RUN - NO CHANGES WERE MADE")
        else:
            report_lines.append("")
            report_lines.append(f"✅ Successfully processed {stats['prices_updated']} price updates")

        # Write enhanced report
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(report_lines))
            self.stdout.write(f"\n📄 Enhanced debug report saved to: {report_file}")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error writing report file: {str(e)}"))

        # Enhanced console summary
        self.stdout.write("\n" + "="*60)
        self.stdout.write("ENHANCED SUMMARY")
        self.stdout.write("="*60)
        for key, value in stats.items():
            if value > 0:
                self.stdout.write(f"{key.replace('_', ' ').title()}: {value}")
        
        if dry_run:
            self.stdout.write(self.style.WARNING("\nThis was a DRY RUN - no changes were made"))
        else:
            self.stdout.write(self.style.SUCCESS(f"\nSuccessfully updated {stats['prices_updated']} prices"))
            
        self.stdout.write(f"\n📄 Detailed debug report: {report_file}")
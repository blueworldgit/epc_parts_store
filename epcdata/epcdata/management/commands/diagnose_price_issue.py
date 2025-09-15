"""
Django management command to diagnose price update issues.
This script investigates why price updates appear successful but the website shows different prices.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import connection
from decimal import Decimal
import json

from oscar.apps.catalogue.models import Product
from oscar.apps.partner.models import StockRecord


class Command(BaseCommand):
    help = 'Diagnose price update issues for specific SKUs'

    def add_arguments(self, parser):
        parser.add_argument(
            'sku',
            type=str,
            help='SKU to diagnose (e.g., C00287967)'
        )
        parser.add_argument(
            '--output-file',
            type=str,
            help='Save diagnostic output to file'
        )
        parser.add_argument(
            '--check-all-prices',
            action='store_true',
            help='Check all price-related fields and relationships'
        )

    def handle(self, *args, **options):
        sku = options['sku']
        output_file = options.get('output_file')
        check_all = options.get('check_all_prices', False)
        
        self.stdout.write("="*80)
        self.stdout.write(f"PRICE DIAGNOSTIC REPORT FOR SKU: {sku}")
        self.stdout.write("="*80)
        self.stdout.write(f"Generated: {timezone.now()}")
        self.stdout.write("")
        
        report_lines = []
        report_lines.append("="*80)
        report_lines.append(f"PRICE DIAGNOSTIC REPORT FOR SKU: {sku}")
        report_lines.append("="*80)
        report_lines.append(f"Generated: {timezone.now()}")
        report_lines.append("")
        
        try:
            # 1. Find all products with this SKU
            self.add_section(report_lines, "1. PRODUCT SEARCH RESULTS")
            products = Product.objects.filter(upc=sku)
            
            if not products.exists():
                msg = f"❌ No products found with SKU: {sku}"
                self.stdout.write(self.style.ERROR(msg))
                report_lines.append(msg)
                return
            
            msg = f"✅ Found {products.count()} product(s) with SKU: {sku}"
            self.stdout.write(self.style.SUCCESS(msg))
            report_lines.append(msg)
            report_lines.append("")
            
            # 2. Analyze each product
            for i, product in enumerate(products, 1):
                self.add_section(report_lines, f"2.{i} PRODUCT ANALYSIS - ID: {product.id}")
                
                # Basic product info
                product_info = [
                    f"Product ID: {product.id}",
                    f"Title: {product.title}",
                    f"UPC/SKU: {product.upc}",
                    f"Product Class: {product.product_class}",
                    f"Structure: {product.structure}",
                    f"Is Parent: {product.is_parent}",
                    f"Parent ID: {product.parent_id if product.parent else 'None'}",
                    f"Date Created: {product.date_created}",
                    f"Date Updated: {product.date_updated}",
                ]
                
                for info in product_info:
                    self.stdout.write(f"  {info}")
                    report_lines.append(f"  {info}")
                report_lines.append("")
                
                # 3. Stock Records Analysis
                self.add_section(report_lines, f"3.{i} STOCK RECORDS ANALYSIS")
                stock_records = StockRecord.objects.filter(product=product)
                
                if not stock_records.exists():
                    msg = f"  ❌ No stock records found for product {product.id}"
                    self.stdout.write(self.style.WARNING(msg))
                    report_lines.append(msg)
                else:
                    msg = f"  ✅ Found {stock_records.count()} stock record(s)"
                    self.stdout.write(self.style.SUCCESS(msg))
                    report_lines.append(msg)
                    
                    for j, stock in enumerate(stock_records, 1):
                        stock_info = [
                            f"    Stock Record {j}:",
                            f"      ID: {stock.id}",
                            f"      Partner: {stock.partner}",
                            f"      Partner SKU: {stock.partner_sku}",
                            f"      Price: £{stock.price or 'None'}",
                            f"      Currency: {getattr(stock, 'currency', 'GBP')}",
                            f"      Cost Price: £{getattr(stock, 'cost_price', 'None') or 'None'}",
                            f"      Num in Stock: {getattr(stock, 'num_in_stock', 'Unknown')}",
                            f"      Low Stock Threshold: {getattr(stock, 'low_stock_threshold', 'Unknown')}",
                            f"      Price Updated Flag: {getattr(stock, 'price_updated', 'Unknown')}",
                            f"      Date Created: {stock.date_created}",
                            f"      Date Updated: {stock.date_updated}",
                        ]
                        
                        for info in stock_info:
                            self.stdout.write(info)
                            report_lines.append(info)
                        report_lines.append("")
                
                # 4. Price Strategy Analysis
                self.add_section(report_lines, f"4.{i} PRICE STRATEGY ANALYSIS")
                
                # Check if product has a price strategy
                try:
                    strategy = product.stockrecords.first().price if product.stockrecords.exists() else None
                    if strategy:
                        msg = f"  ✅ Primary price strategy: £{strategy}"
                        self.stdout.write(self.style.SUCCESS(msg))
                        report_lines.append(msg)
                    else:
                        msg = f"  ❌ No price strategy found"
                        self.stdout.write(self.style.WARNING(msg))
                        report_lines.append(msg)
                except Exception as e:
                    msg = f"  ❌ Error getting price strategy: {str(e)}"
                    self.stdout.write(self.style.ERROR(msg))
                    report_lines.append(msg)
                
                # 5. Template Context Analysis
                self.add_section(report_lines, f"5.{i} TEMPLATE CONTEXT ANALYSIS")
                
                # Simulate what the template would see
                try:
                    # Check what price the product.price property returns
                    product_price = product.stockrecords.first().price if product.stockrecords.exists() else None
                    if product_price:
                        msg = f"  Product.stockrecords.first().price: £{product_price}"
                        self.stdout.write(msg)
                        report_lines.append(msg)
                    
                    # Check if there are multiple stock records with different prices
                    if stock_records.count() > 1:
                        prices = [sr.price for sr in stock_records if sr.price]
                        unique_prices = set(prices)
                        if len(unique_prices) > 1:
                            msg = f"  ⚠️  WARNING: Multiple different prices found: {list(unique_prices)}"
                            self.stdout.write(self.style.WARNING(msg))
                            report_lines.append(msg)
                        else:
                            msg = f"  ✅ All stock records have same price: £{prices[0] if prices else 'None'}"
                            self.stdout.write(msg)
                            report_lines.append(msg)
                
                except Exception as e:
                    msg = f"  ❌ Error in template context analysis: {str(e)}"
                    self.stdout.write(self.style.ERROR(msg))
                    report_lines.append(msg)
                
                report_lines.append("")
            
            # 6. Database Query Analysis
            self.add_section(report_lines, "6. DATABASE QUERY ANALYSIS")
            
            # Raw SQL to check what's actually in the database
            with connection.cursor() as cursor:
                # Check products table
                cursor.execute("""
                    SELECT id, title, upc, date_created, date_updated 
                    FROM catalogue_product 
                    WHERE upc = %s
                """, [sku])
                
                db_products = cursor.fetchall()
                msg = f"Raw DB query found {len(db_products)} products:"
                self.stdout.write(msg)
                report_lines.append(msg)
                
                for product_row in db_products:
                    product_info = f"  Product ID {product_row[0]}: {product_row[1]} (Created: {product_row[3]}, Updated: {product_row[4]})"
                    self.stdout.write(product_info)
                    report_lines.append(product_info)
                
                # Check stock records table
                cursor.execute("""
                    SELECT sr.id, sr.product_id, sr.partner_sku, sr.price, 
                           sr.date_created, sr.date_updated, p.name as partner_name
                    FROM partner_stockrecord sr
                    JOIN partner_partner p ON sr.partner_id = p.id
                    JOIN catalogue_product cp ON sr.product_id = cp.id
                    WHERE cp.upc = %s
                    ORDER BY sr.date_updated DESC
                """, [sku])
                
                stock_rows = cursor.fetchall()
                msg = f"\nRaw DB query found {len(stock_rows)} stock records:"
                self.stdout.write(msg)
                report_lines.append("")
                report_lines.append(msg)
                
                for stock_row in stock_rows:
                    stock_info = f"  Stock ID {stock_row[0]}: Product {stock_row[1]}, Price £{stock_row[3]}, Partner: {stock_row[6]}, Updated: {stock_row[5]}"
                    self.stdout.write(stock_info)
                    report_lines.append(stock_info)
            
            # 7. Cache and Session Analysis
            self.add_section(report_lines, "7. CACHE AND SESSION ANALYSIS")
            
            # Check if there might be caching issues
            cache_checks = [
                "Django cache framework status",
                "Template fragment caching",
                "Database query caching",
                "Static file caching",
            ]
            
            msg = "Potential caching layers to investigate:"
            self.stdout.write(msg)
            report_lines.append(msg)
            
            for check in cache_checks:
                check_msg = f"  • {check}"
                self.stdout.write(check_msg)
                report_lines.append(check_msg)
            
            # 8. Recommendations
            self.add_section(report_lines, "8. RECOMMENDATIONS")
            
            recommendations = [
                "1. Check if there are multiple stock records with different prices",
                "2. Verify the template is using the correct price field",
                "3. Check for any caching that might be serving old prices",
                "4. Ensure the price update script is updating the correct stock record",
                "5. Check if there are any custom price strategies or middleware affecting pricing",
                "6. Verify the product being updated matches the product being displayed",
            ]
            
            for rec in recommendations:
                self.stdout.write(rec)
                report_lines.append(rec)
            
            # 9. Next Steps
            self.add_section(report_lines, "9. SUGGESTED NEXT STEPS")
            
            next_steps = [
                f"1. Run: python manage.py shell",
                f"2. Execute: Product.objects.filter(upc='{sku}').first().stockrecords.all()",
                f"3. Check: StockRecord.objects.filter(product__upc='{sku}').order_by('-date_updated')",
                f"4. Verify: Clear any caches and check the website again",
                f"5. Test: Update the price manually in Django admin and verify it appears on site",
            ]
            
            for step in next_steps:
                self.stdout.write(step)
                report_lines.append(step)
            
        except Exception as e:
            error_msg = f"❌ Unexpected error during diagnosis: {str(e)}"
            self.stdout.write(self.style.ERROR(error_msg))
            report_lines.append(error_msg)
            import traceback
            traceback_info = traceback.format_exc()
            self.stdout.write(traceback_info)
            report_lines.append(traceback_info)
        
        # Save to file if requested
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(report_lines))
                self.stdout.write(f"\n📄 Diagnostic report saved to: {output_file}")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error saving report: {str(e)}"))
        
        self.stdout.write("\n" + "="*80)
        self.stdout.write("DIAGNOSTIC COMPLETE")
        self.stdout.write("="*80)

    def add_section(self, report_lines, title):
        """Add a section header to both stdout and report"""
        self.stdout.write(f"\n{title}")
        self.stdout.write("-" * len(title))
        report_lines.append(title)
        report_lines.append("-" * len(title))
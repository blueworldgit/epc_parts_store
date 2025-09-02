"""
Django management command to check Oscar database for products with no pricing.
This command identifies all Oscar products that have missing or zero prices in their StockRecord.

Usage:
    python manage.py check_oscar_pricing
    python manage.py check_oscar_pricing --verbose
    python manage.py check_oscar_pricing --export-report
"""

import os
from datetime import datetime
from django.core.management.base import BaseCommand
from django.db.models import Q
from oscar.apps.catalogue.models import Product
from oscar.apps.partner.models import StockRecord


class Command(BaseCommand):
    help = 'Check Oscar database for products with no pricing data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed information for each product'
        )
        parser.add_argument(
            '--export-report',
            action='store_true',
            help='Export detailed report to oscar_pricing_report.txt'
        )
        parser.add_argument(
            '--include-zero-price',
            action='store_true',
            help='Include products with zero price (default: only missing prices)'
        )

    def handle(self, *args, **options):
        verbose = options['verbose']
        export_report = options['export_report']
        include_zero_price = options['include_zero_price']

        self.stdout.write("🔍 Checking Oscar database for pricing issues...")
        self.stdout.write("=" * 60)
        
        # Set up output file path similar to check_updated_parts
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        output_file_path = os.path.join(base_dir, 'nopricing.txt')
        self.stdout.write(f"Output will be saved to: {output_file_path}")

        # Get all Oscar products
        all_products = Product.objects.all()
        total_products = all_products.count()

        # Statistics tracking
        stats = {
            'total_products': total_products,
            'products_with_pricing': 0,
            'products_no_stock_record': 0,
            'products_no_price': 0,
            'products_zero_price': 0,
            'products_valid_price': 0
        }

        # Lists for detailed reporting
        no_stock_record = []
        no_price = []
        zero_price = []

        self.stdout.write(f"📊 Total Oscar products found: {total_products:,}")

        if total_products == 0:
            self.stdout.write(self.style.WARNING("No Oscar products found in database"))
            return

        # Analyze each product
        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            output_file.write(f"Oscar Products with No/Zero Pricing Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            output_file.write("=" * 80 + "\n\n")
            output_file.write(f"Total Oscar products found: {total_products:,}\n\n")
            
            # First section: Products with no stock record
            output_file.write("PRODUCTS WITH NO STOCK RECORD:\n")
            output_file.write("-" * 40 + "\n")
            
            for product in all_products:
                # Get stock record for this product
                stock_record = StockRecord.objects.filter(product=product).first()
                
                if not stock_record:
                    # No stock record at all
                    stats['products_no_stock_record'] += 1
                    no_stock_record.append(product)
                    product_code = product.upc or 'None'
                    output_file.write(f"{product_code}\n")
                    if verbose:
                        self.stdout.write(f"❌ {product.title[:50]} (SKU: {product_code}) - No stock record")
            
            output_file.write(f"\nTotal products with NO STOCK RECORD: {stats['products_no_stock_record']}\n\n")
            
            # Second section: Products with no price (None)
            output_file.write("PRODUCTS WITH NO PRICE (None):\n")
            output_file.write("-" * 40 + "\n")
            
            for product in all_products:
                stock_record = StockRecord.objects.filter(product=product).first()
                
                if stock_record and stock_record.price is None:
                    # Price is explicitly None
                    stats['products_no_price'] += 1
                    no_price.append((product, stock_record))
                    product_code = product.upc or 'None'
                    output_file.write(f"{product_code}\n")
                    if verbose:
                        self.stdout.write(f"💰 {product.title[:50]} (SKU: {product_code}) - Price is None")
            
            output_file.write(f"\nTotal products with NO PRICE: {stats['products_no_price']}\n\n")
            
            # Third section: Products with zero price (if requested)
            if include_zero_price:
                output_file.write("PRODUCTS WITH ZERO PRICE:\n")
                output_file.write("-" * 40 + "\n")
                
                for product in all_products:
                    stock_record = StockRecord.objects.filter(product=product).first()
                    
                    if stock_record and stock_record.price == 0:
                        # Price is zero
                        stats['products_zero_price'] += 1
                        zero_price.append((product, stock_record))
                        product_code = product.upc or 'None'
                        output_file.write(f"{product_code}\n")
                        if verbose:
                            self.stdout.write(f"🆓 {product.title[:50]} (SKU: {product_code}) - Price is £0.00")
                
                output_file.write(f"\nTotal products with ZERO PRICE: {stats['products_zero_price']}\n\n")
            
            # Count valid prices for stats
            for product in all_products:
                stock_record = StockRecord.objects.filter(product=product).first()
                
                if stock_record and stock_record.price is not None and stock_record.price > 0:
                    stats['products_valid_price'] += 1
                    if verbose:
                        self.stdout.write(f"✅ {product.title[:50]} (SKU: {product.upc or 'None'}) - Price: £{stock_record.price}")
            
            # Summary at end of file
            output_file.write("SUMMARY:\n")
            output_file.write("-" * 20 + "\n")
            output_file.write(f"Total products: {stats['total_products']}\n")
            output_file.write(f"Products with no stock record: {stats['products_no_stock_record']}\n")
            output_file.write(f"Products with no price (None): {stats['products_no_price']}\n")
            if include_zero_price:
                output_file.write(f"Products with zero price: {stats['products_zero_price']}\n")
            output_file.write(f"Products with valid pricing: {stats['products_valid_price']}\n")
            output_file.write(f"Report generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # Calculate totals
        stats['products_with_pricing'] = stats['products_valid_price']
        if not include_zero_price:
            stats['products_with_pricing'] += stats['products_zero_price']

        # Display summary
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("📈 OSCAR PRICING ANALYSIS SUMMARY")
        self.stdout.write("=" * 60)
        self.stdout.write(f"Total products: {stats['total_products']:,}")
        self.stdout.write(f"Products with valid pricing: {stats['products_valid_price']:,}")
        self.stdout.write(f"Products with zero price: {stats['products_zero_price']:,}")
        self.stdout.write(f"Products with no price (None): {stats['products_no_price']:,}")
        self.stdout.write(f"Products with no stock record: {stats['products_no_stock_record']:,}")
        
        # Show file output info
        self.stdout.write(f"\n📝 Product codes saved to: {output_file_path}")

        # Show percentages
        if total_products > 0:
            valid_pct = (stats['products_valid_price'] / total_products) * 100
            issues_count = stats['products_no_price'] + stats['products_no_stock_record']
            if include_zero_price:
                issues_count += stats['products_zero_price']
            issues_pct = (issues_count / total_products) * 100
            
            self.stdout.write(f"\n📊 PRICING HEALTH:")
            self.stdout.write(f"✅ Valid pricing: {valid_pct:.1f}%")
            self.stdout.write(f"❌ Pricing issues: {issues_pct:.1f}%")

        # Export detailed report if requested
        if export_report:
            self._export_detailed_report(stats, no_stock_record, no_price, zero_price, include_zero_price)

        # Show recommendations
        self._show_recommendations(stats)

    def _export_detailed_report(self, stats, no_stock_record, no_price, zero_price, include_zero_price):
        """Export detailed report to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = f'oscar_pricing_report_{timestamp}.txt'
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"Oscar Pricing Analysis Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            
            # Summary
            f.write("SUMMARY:\n")
            f.write(f"Total products: {stats['total_products']:,}\n")
            f.write(f"Products with valid pricing: {stats['products_valid_price']:,}\n")
            f.write(f"Products with zero price: {stats['products_zero_price']:,}\n")
            f.write(f"Products with no price (None): {stats['products_no_price']:,}\n")
            f.write(f"Products with no stock record: {stats['products_no_stock_record']:,}\n\n")
            
            # Products with no stock record
            if no_stock_record:
                f.write("PRODUCTS WITH NO STOCK RECORD:\n")
                f.write("-" * 50 + "\n")
                for product in no_stock_record:
                    f.write(f"SKU: {product.upc or 'None':<15} | Title: {product.title}\n")
                f.write(f"\nTotal: {len(no_stock_record)} products\n\n")
            
            # Products with no price (None)
            if no_price:
                f.write("PRODUCTS WITH NO PRICE (None):\n")
                f.write("-" * 50 + "\n")
                for product, stock_record in no_price:
                    f.write(f"SKU: {product.upc or 'None':<15} | Title: {product.title}\n")
                f.write(f"\nTotal: {len(no_price)} products\n\n")
            
            # Products with zero price (if including them as issues)
            if zero_price and include_zero_price:
                f.write("PRODUCTS WITH ZERO PRICE:\n")
                f.write("-" * 50 + "\n")
                for product, stock_record in zero_price:
                    f.write(f"SKU: {product.upc or 'None':<15} | Title: {product.title}\n")
                f.write(f"\nTotal: {len(zero_price)} products\n\n")
            
            f.write(f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        self.stdout.write(f"\n📝 Detailed report exported to: {report_file}")

    def _show_recommendations(self, stats):
        """Show recommendations based on findings"""
        self.stdout.write("\n" + "💡 RECOMMENDATIONS:")
        
        if stats['products_no_stock_record'] > 0:
            self.stdout.write(f"• Create stock records for {stats['products_no_stock_record']} products with missing stock data")
        
        if stats['products_no_price'] > 0:
            self.stdout.write(f"• Set prices for {stats['products_no_price']} products with None price")
        
        if stats['products_zero_price'] > 0:
            self.stdout.write(f"• Review {stats['products_zero_price']} products with £0.00 price (may be intentional)")
        
        if stats['products_no_stock_record'] > 0 or stats['products_no_price'] > 0:
            self.stdout.write("\n🔧 SUGGESTED ACTIONS:")
            self.stdout.write("1. Run price update from Excel: python manage.py update_prices_from_excel")
            self.stdout.write("2. Check import scripts: python manage.py import_to_oscar --dry-run")
            self.stdout.write("3. Verify product creation process includes stock records")

        if stats['products_valid_price'] == stats['total_products']:
            self.stdout.write("🎉 All products have valid pricing! No action needed.")

"""
Django management command to check Oscar database for products with stock issues.
This command identifies all Oscar products that have stock levels of 0, > 0, or stock errors.

Usage:
    python manage.py check_oscar_stock
    python manage.py check_oscar_stock --verbose
    python manage.py check_oscar_stock --export-report
"""

import os
from datetime import datetime
from django.core.management.base import BaseCommand
from django.db.models import Q
from oscar.apps.catalogue.models import Product
from oscar.apps.partner.models import Partner, StockRecord


class Command(BaseCommand):
    help = 'Check Oscar database for products with stock level issues'

    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed information for each product'
        )
        parser.add_argument(
            '--export-report',
            action='store_true',
            help='Export detailed report to oscar_stock_report.txt'
        )
        parser.add_argument(
            '--include-positive-stock',
            action='store_true',
            help='Include products with positive stock in the output file (default: only zero/error stock)'
        )

    def handle(self, *args, **options):
        verbose = options['verbose']
        export_report = options['export_report']
        include_positive_stock = options['include_positive_stock']

        self.stdout.write("🔍 Checking Oscar database for stock level issues...")
        self.stdout.write("=" * 60)
        
        # Set up output file path similar to check_updated_parts
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        output_file_path = os.path.join(base_dir, 'stockreport.txt')
        self.stdout.write(f"Output will be saved to: {output_file_path}")

        # Get all Oscar products
        all_products = Product.objects.all()
        total_products = all_products.count()

        # Statistics tracking
        stats = {
            'total_products': total_products,
            'products_no_stock_record': 0,
            'products_zero_stock': 0,
            'products_positive_stock': 0,
            'products_negative_stock': 0,
            'products_null_stock': 0,
            'products_pricing_no_stock': 0,
            'products_no_pricing_no_stock': 0
        }

        # Lists for detailed reporting
        no_stock_record = []
        zero_stock = []
        positive_stock = []
        negative_stock = []
        null_stock = []
        pricing_no_stock = []
        no_pricing_no_stock = []

        self.stdout.write(f"📊 Total Oscar products found: {total_products:,}")

        if total_products == 0:
            self.stdout.write(self.style.WARNING("No Oscar products found in database"))
            return

        # Analyze each product
        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            output_file.write(f"Oscar Products Stock Level Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
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
            
            # Second section: Products with null stock
            output_file.write("PRODUCTS WITH NULL STOCK:\n")
            output_file.write("-" * 40 + "\n")
            
            for product in all_products:
                stock_record = StockRecord.objects.filter(product=product).first()
                
                if stock_record and stock_record.num_in_stock is None:
                    # Stock is explicitly None
                    stats['products_null_stock'] += 1
                    null_stock.append((product, stock_record))
                    product_code = product.upc or 'None'
                    output_file.write(f"{product_code}\n")
                    if verbose:
                        self.stdout.write(f"❓ {product.title[:50]} (SKU: {product_code}) - Stock is None")
            
            output_file.write(f"\nTotal products with NULL STOCK: {stats['products_null_stock']}\n\n")
            
            # Third section: Products with zero stock
            output_file.write("PRODUCTS WITH ZERO STOCK:\n")
            output_file.write("-" * 40 + "\n")
            
            for product in all_products:
                stock_record = StockRecord.objects.filter(product=product).first()
                
                if stock_record and stock_record.num_in_stock == 0:
                    # Stock is zero
                    stats['products_zero_stock'] += 1
                    zero_stock.append((product, stock_record))
                    product_code = product.upc or 'None'
                    output_file.write(f"{product_code}\n")
                    if verbose:
                        self.stdout.write(f"🆓 {product.title[:50]} (SKU: {product_code}) - Stock is 0")
            
            output_file.write(f"\nTotal products with ZERO STOCK: {stats['products_zero_stock']}\n\n")
            
            # Fourth section: Products with negative stock (stock errors)
            output_file.write("PRODUCTS WITH NEGATIVE STOCK (ERRORS):\n")
            output_file.write("-" * 40 + "\n")
            
            for product in all_products:
                stock_record = StockRecord.objects.filter(product=product).first()
                
                if stock_record and stock_record.num_in_stock is not None and stock_record.num_in_stock < 0:
                    # Stock is negative (error condition)
                    stats['products_negative_stock'] += 1
                    negative_stock.append((product, stock_record))
                    product_code = product.upc or 'None'
                    output_file.write(f"{product_code}\n")
                    if verbose:
                        self.stdout.write(f"⚠️ {product.title[:50]} (SKU: {product_code}) - Stock is {stock_record.num_in_stock}")
            
            output_file.write(f"\nTotal products with NEGATIVE STOCK: {stats['products_negative_stock']}\n\n")
            
            # Fifth section: Products with pricing but no stock (0 or null stock but has price)
            output_file.write("PRODUCTS WITH PRICING BUT NO STOCK:\n")
            output_file.write("-" * 40 + "\n")
            
            for product in all_products:
                stock_record = StockRecord.objects.filter(product=product).first()
                
                if stock_record:
                    # Check if product has pricing but no stock
                    has_price = stock_record.price is not None and stock_record.price > 0
                    has_no_stock = (stock_record.num_in_stock is None or stock_record.num_in_stock == 0)
                    
                    if has_price and has_no_stock:
                        stats['products_pricing_no_stock'] += 1
                        pricing_no_stock.append((product, stock_record))
                        product_code = product.upc or 'None'
                        price_display = f"£{stock_record.price}" if stock_record.price else "£0"
                        stock_display = stock_record.num_in_stock if stock_record.num_in_stock is not None else "None"
                        output_file.write(f"{product_code}\n")
                        if verbose:
                            self.stdout.write(f"💰📦 {product.title[:50]} (SKU: {product_code}) - Price: {price_display}, Stock: {stock_display}")
            
            output_file.write(f"\nTotal products with PRICING BUT NO STOCK: {stats['products_pricing_no_stock']}\n\n")
            
            # Sixth section: Products with no pricing and no stock
            output_file.write("PRODUCTS WITH NO PRICING AND NO STOCK:\n")
            output_file.write("-" * 40 + "\n")
            
            for product in all_products:
                stock_record = StockRecord.objects.filter(product=product).first()
                
                if stock_record:
                    # Check if product has no pricing and no stock
                    has_no_price = (stock_record.price is None or stock_record.price == 0)
                    has_no_stock = (stock_record.num_in_stock is None or stock_record.num_in_stock == 0)
                    
                    if has_no_price and has_no_stock:
                        stats['products_no_pricing_no_stock'] += 1
                        no_pricing_no_stock.append((product, stock_record))
                        product_code = product.upc or 'None'
                        price_display = f"£{stock_record.price}" if stock_record.price else "None/£0"
                        stock_display = stock_record.num_in_stock if stock_record.num_in_stock is not None else "None"
                        output_file.write(f"{product_code}\n")
                        if verbose:
                            self.stdout.write(f"❌❌ {product.title[:50]} (SKU: {product_code}) - Price: {price_display}, Stock: {stock_display}")
            
            output_file.write(f"\nTotal products with NO PRICING AND NO STOCK: {stats['products_no_pricing_no_stock']}\n\n")
            
            # Seventh section: Products with positive stock (if requested)
            if include_positive_stock:
                output_file.write("PRODUCTS WITH POSITIVE STOCK:\n")
                output_file.write("-" * 40 + "\n")
                
                for product in all_products:
                    stock_record = StockRecord.objects.filter(product=product).first()
                    
                    if stock_record and stock_record.num_in_stock is not None and stock_record.num_in_stock > 0:
                        # Stock is positive
                        stats['products_positive_stock'] += 1
                        positive_stock.append((product, stock_record))
                        product_code = product.upc or 'None'
                        output_file.write(f"{product_code}\n")
                        if verbose:
                            self.stdout.write(f"✅ {product.title[:50]} (SKU: {product_code}) - Stock: {stock_record.num_in_stock}")
                
                output_file.write(f"\nTotal products with POSITIVE STOCK: {stats['products_positive_stock']}\n\n")
            else:
                # Count positive stock for stats but don't output to file
                for product in all_products:
                    stock_record = StockRecord.objects.filter(product=product).first()
                    
                    if stock_record and stock_record.num_in_stock is not None and stock_record.num_in_stock > 0:
                        stats['products_positive_stock'] += 1
                        if verbose:
                            self.stdout.write(f"✅ {product.title[:50]} (SKU: {product.upc or 'None'}) - Stock: {stock_record.num_in_stock}")
            
            # Summary at end of file
            output_file.write("SUMMARY:\n")
            output_file.write("-" * 20 + "\n")
            output_file.write(f"Total products: {stats['total_products']}\n")
            output_file.write(f"Products with no stock record: {stats['products_no_stock_record']}\n")
            output_file.write(f"Products with null stock: {stats['products_null_stock']}\n")
            output_file.write(f"Products with zero stock: {stats['products_zero_stock']}\n")
            output_file.write(f"Products with negative stock (errors): {stats['products_negative_stock']}\n")
            output_file.write(f"Products with pricing but no stock: {stats['products_pricing_no_stock']}\n")
            output_file.write(f"Products with no pricing and no stock: {stats['products_no_pricing_no_stock']}\n")
            output_file.write(f"Products with positive stock: {stats['products_positive_stock']}\n")
            output_file.write(f"Report generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # Display summary
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("📈 OSCAR STOCK ANALYSIS SUMMARY")
        self.stdout.write("=" * 60)
        self.stdout.write(f"Total products: {stats['total_products']:,}")
        self.stdout.write(f"Products with positive stock: {stats['products_positive_stock']:,}")
        self.stdout.write(f"Products with zero stock: {stats['products_zero_stock']:,}")
        self.stdout.write(f"Products with null stock: {stats['products_null_stock']:,}")
        self.stdout.write(f"Products with negative stock (errors): {stats['products_negative_stock']:,}")
        self.stdout.write(f"Products with no stock record: {stats['products_no_stock_record']:,}")
        self.stdout.write(f"Products with pricing but no stock: {stats['products_pricing_no_stock']:,}")
        self.stdout.write(f"Products with no pricing and no stock: {stats['products_no_pricing_no_stock']:,}")
        
        # Show file output info
        self.stdout.write(f"\n📝 Product codes saved to: {output_file_path}")

        # Show percentages
        if total_products > 0:
            positive_pct = (stats['products_positive_stock'] / total_products) * 100
            issues_count = stats['products_zero_stock'] + stats['products_null_stock'] + stats['products_negative_stock'] + stats['products_no_stock_record']
            issues_pct = (issues_count / total_products) * 100
            
            self.stdout.write(f"\n📊 STOCK HEALTH:")
            self.stdout.write(f"✅ Products with stock: {positive_pct:.1f}%")
            self.stdout.write(f"❌ Stock issues: {issues_pct:.1f}%")

        # Export detailed report if requested
        if export_report:
            self._export_detailed_report(stats, no_stock_record, null_stock, zero_stock, negative_stock, positive_stock, pricing_no_stock, no_pricing_no_stock, include_positive_stock)

        # Show recommendations
        self._show_recommendations(stats)

    def _export_detailed_report(self, stats, no_stock_record, null_stock, zero_stock, negative_stock, positive_stock, pricing_no_stock, no_pricing_no_stock, include_positive_stock):
        """Export detailed report to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = f'oscar_stock_report_{timestamp}.txt'
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"Oscar Stock Analysis Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            
            # Summary
            f.write("SUMMARY:\n")
            f.write(f"Total products: {stats['total_products']:,}\n")
            f.write(f"Products with positive stock: {stats['products_positive_stock']:,}\n")
            f.write(f"Products with zero stock: {stats['products_zero_stock']:,}\n")
            f.write(f"Products with null stock: {stats['products_null_stock']:,}\n")
            f.write(f"Products with negative stock (errors): {stats['products_negative_stock']:,}\n")
            f.write(f"Products with no stock record: {stats['products_no_stock_record']:,}\n")
            f.write(f"Products with pricing but no stock: {stats['products_pricing_no_stock']:,}\n")
            f.write(f"Products with no pricing and no stock: {stats['products_no_pricing_no_stock']:,}\n\n")
            
            # Products with no stock record
            if no_stock_record:
                f.write("PRODUCTS WITH NO STOCK RECORD:\n")
                f.write("-" * 50 + "\n")
                for product in no_stock_record:
                    f.write(f"SKU: {product.upc or 'None':<15} | Title: {product.title}\n")
                f.write(f"\nTotal: {len(no_stock_record)} products\n\n")
            
            # Products with null stock
            if null_stock:
                f.write("PRODUCTS WITH NULL STOCK:\n")
                f.write("-" * 50 + "\n")
                for product, stock_record in null_stock:
                    f.write(f"SKU: {product.upc or 'None':<15} | Title: {product.title}\n")
                f.write(f"\nTotal: {len(null_stock)} products\n\n")
            
            # Products with zero stock
            if zero_stock:
                f.write("PRODUCTS WITH ZERO STOCK:\n")
                f.write("-" * 50 + "\n")
                for product, stock_record in zero_stock:
                    f.write(f"SKU: {product.upc or 'None':<15} | Title: {product.title}\n")
                f.write(f"\nTotal: {len(zero_stock)} products\n\n")
            
            # Products with negative stock (errors)
            if negative_stock:
                f.write("PRODUCTS WITH NEGATIVE STOCK (ERRORS):\n")
                f.write("-" * 50 + "\n")
                for product, stock_record in negative_stock:
                    f.write(f"SKU: {product.upc or 'None':<15} | Stock: {stock_record.num_in_stock} | Title: {product.title}\n")
                f.write(f"\nTotal: {len(negative_stock)} products\n\n")
            
            # Products with pricing but no stock
            if pricing_no_stock:
                f.write("PRODUCTS WITH PRICING BUT NO STOCK:\n")
                f.write("-" * 50 + "\n")
                for product, stock_record in pricing_no_stock:
                    price_display = f"£{stock_record.price}" if stock_record.price else "£0"
                    stock_display = stock_record.num_in_stock if stock_record.num_in_stock is not None else "None"
                    f.write(f"SKU: {product.upc or 'None':<15} | Price: {price_display:<10} | Stock: {stock_display} | Title: {product.title}\n")
                f.write(f"\nTotal: {len(pricing_no_stock)} products\n\n")
            
            # Products with no pricing and no stock
            if no_pricing_no_stock:
                f.write("PRODUCTS WITH NO PRICING AND NO STOCK:\n")
                f.write("-" * 50 + "\n")
                for product, stock_record in no_pricing_no_stock:
                    price_display = f"£{stock_record.price}" if stock_record.price else "None/£0"
                    stock_display = stock_record.num_in_stock if stock_record.num_in_stock is not None else "None"
                    f.write(f"SKU: {product.upc or 'None':<15} | Price: {price_display:<10} | Stock: {stock_display} | Title: {product.title}\n")
                f.write(f"\nTotal: {len(no_pricing_no_stock)} products\n\n")
            
            # Products with positive stock (if including them)
            if positive_stock and include_positive_stock:
                f.write("PRODUCTS WITH POSITIVE STOCK:\n")
                f.write("-" * 50 + "\n")
                for product, stock_record in positive_stock:
                    f.write(f"SKU: {product.upc or 'None':<15} | Stock: {stock_record.num_in_stock} | Title: {product.title}\n")
                f.write(f"\nTotal: {len(positive_stock)} products\n\n")
            
            f.write(f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        self.stdout.write(f"\n📝 Detailed report exported to: {report_file}")

    def _show_recommendations(self, stats):
        """Show recommendations based on findings"""
        self.stdout.write("\n" + "💡 RECOMMENDATIONS:")
        
        if stats['products_no_stock_record'] > 0:
            self.stdout.write(f"• Create stock records for {stats['products_no_stock_record']} products with missing stock data")
        
        if stats['products_null_stock'] > 0:
            self.stdout.write(f"• Set stock levels for {stats['products_null_stock']} products with null stock")
        
        if stats['products_negative_stock'] > 0:
            self.stdout.write(f"• Fix {stats['products_negative_stock']} products with negative stock (data errors)")
        
        if stats['products_zero_stock'] > 0:
            self.stdout.write(f"• Review {stats['products_zero_stock']} products with zero stock (may need restocking)")
        
        if stats['products_pricing_no_stock'] > 0:
            self.stdout.write(f"• Consider restocking {stats['products_pricing_no_stock']} products that have pricing but no stock")
        
        if stats['products_no_pricing_no_stock'] > 0:
            self.stdout.write(f"• Review {stats['products_no_pricing_no_stock']} products with no pricing and no stock (may be discontinued)")
        
        if stats['products_no_stock_record'] > 0 or stats['products_null_stock'] > 0 or stats['products_negative_stock'] > 0:
            self.stdout.write("\n🔧 SUGGESTED ACTIONS:")
            self.stdout.write("1. Run stock update from source: python manage.py update_stock_levels")
            self.stdout.write("2. Check import scripts: python manage.py import_to_oscar --dry-run")
            self.stdout.write("3. Verify product creation process includes stock records")
            self.stdout.write("4. Investigate negative stock values for data consistency")
            
        if stats['products_pricing_no_stock'] > 0:
            self.stdout.write("5. Consider automatic reordering for products with pricing but no stock")
            
        if stats['products_no_pricing_no_stock'] > 0:
            self.stdout.write("6. Review products with no pricing and no stock for discontinuation")

        if stats['products_positive_stock'] == stats['total_products']:
            self.stdout.write("🎉 All products have positive stock levels! No action needed.")

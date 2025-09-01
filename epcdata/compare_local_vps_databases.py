#!/usr/bin/env python3
"""
Database Comparison Script: Local vs VPS
========================================

This script compares the local development database with the VPS production database
to diagnose why some products do not have pricing and stock information.

Usage:
    python compare_local_vps_databases.py

Dependencies:
    - psycopg2 (already installed)
    - Access to both local and VPS PostgreSQL databases
"""

import psycopg2
import sys
from decimal import Decimal
from collections import defaultdict
import json

# Database Configuration
LOCAL_DB_CONFIG = {
    'host': 'localhost',
    'database': 'vansdirect',
    'user': 'postgres',
    'password': 'letmein123',
    'port': '5432'
}

VPS_DB_CONFIG = {
    'host': '80.95.207.42',  # VPS IP
    'database': 'parts_store',
    'user': 'postgres',
    'password': 'N0rwich!',
    'port': '5432'
}

class DatabaseComparator:
    def __init__(self):
        self.local_conn = None
        self.vps_conn = None
        self.results = {
            'local_stats': {},
            'vps_stats': {},
            'missing_on_vps': {
                'parts': [],
                'pricing': [],
                'stock': [],
                'oscar_products': []
            },
            'orphaned_on_vps': {
                'pricing': [],
                'stock': [],
                'oscar_products': []
            },
            'mismatched_prices': [],
            'issues_found': []
        }

    def connect_databases(self):
        """Connect to both local and VPS databases"""
        try:
            print("🔌 Connecting to LOCAL database...")
            self.local_conn = psycopg2.connect(**LOCAL_DB_CONFIG)
            print("✅ Local database connected successfully")
            
            print("🔌 Connecting to VPS database...")
            self.vps_conn = psycopg2.connect(**VPS_DB_CONFIG)
            print("✅ VPS database connected successfully")
            
        except psycopg2.Error as e:
            print(f"❌ Database connection error: {e}")
            sys.exit(1)

    def get_table_stats(self, conn, db_name):
        """Get basic statistics for all relevant tables"""
        cursor = conn.cursor()
        stats = {}
        
        tables_to_check = [
            'motorpartsdata_part',
            'motorpartsdata_pricingdata', 
            'catalogue_product',
            'partner_stockrecord'
        ]
        
        for table in tables_to_check:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                stats[table] = count
                print(f"  📊 {db_name} {table}: {count:,} records")
            except psycopg2.Error as e:
                stats[table] = f"Error: {e}"
                print(f"  ❌ {db_name} {table}: Error - {e}")
        
        cursor.close()
        return stats

    def get_parts_data(self, conn):
        """Get all parts from motorpartsdata_part table"""
        cursor = conn.cursor()
        
        query = """
        SELECT id, part_number, usage_name 
        FROM motorpartsdata_part 
        ORDER BY part_number
        """
        
        cursor.execute(query)
        parts = {}
        for row in cursor.fetchall():
            parts[row[1]] = {  # Use part_number as key
                'id': row[0],
                'part_number': row[1],
                'usage_name': row[2]
            }
        
        cursor.close()
        return parts

    def get_pricing_data(self, conn):
        """Get all pricing data"""
        cursor = conn.cursor()
        
        query = """
        SELECT p.part_number, pd.list_price, pd.vor, pd.stock_order
        FROM motorpartsdata_pricingdata pd
        JOIN motorpartsdata_part p ON pd.part_number_id = p.id
        ORDER BY p.part_number
        """
        
        def safe_float_convert(value):
            """Safely convert string with commas to float"""
            if value and value != '':
                try:
                    # Remove commas and convert to float
                    return float(str(value).replace(',', ''))
                except (ValueError, TypeError):
                    return None
            return None
        
        cursor.execute(query)
        pricing = {}
        for row in cursor.fetchall():
            pricing[row[0]] = {
                'list_price': safe_float_convert(row[1]),
                'vor_price': safe_float_convert(row[2]),
                'stock_order_price': safe_float_convert(row[3])
            }
        
        cursor.close()
        return pricing

    def get_oscar_products(self, conn):
        """Get Oscar products and their stock records"""
        cursor = conn.cursor()
        
        # Get products with stock records
        query = """
        SELECT DISTINCT p.upc, p.title, sr.price, sr.num_in_stock
        FROM catalogue_product p
        LEFT JOIN partner_stockrecord sr ON p.id = sr.product_id
        WHERE p.upc IS NOT NULL
        ORDER BY p.upc
        """
        
        cursor.execute(query)
        products = {}
        for row in cursor.fetchall():
            upc = row[0]
            if upc not in products:
                products[upc] = {
                    'title': row[1],
                    'price': float(row[2]) if row[2] else None,
                    'stock': int(row[3]) if row[3] else 0
                }
        
        cursor.close()
        return products

    def compare_parts(self):
        """Compare parts between local and VPS"""
        print("\n📦 Comparing Parts...")
        
        local_parts = self.get_parts_data(self.local_conn)
        vps_parts = self.get_parts_data(self.vps_conn)
        
        print(f"  Local parts: {len(local_parts):,}")
        print(f"  VPS parts: {len(vps_parts):,}")
        
        # Find missing parts on VPS
        missing_parts = []
        for part_num, part_data in local_parts.items():
            if part_num not in vps_parts:
                missing_parts.append(part_data)
        
        self.results['missing_on_vps']['parts'] = missing_parts
        print(f"  ❌ Parts missing on VPS: {len(missing_parts):,}")
        
        if missing_parts:
            print("  📋 Sample missing parts:")
            for part in missing_parts[:5]:
                print(f"    • {part['part_number']} - {part['usage_name']}")
            if len(missing_parts) > 5:
                print(f"    ... and {len(missing_parts) - 5} more")

    def compare_pricing(self):
        """Compare pricing data between local and VPS"""
        print("\n💰 Comparing Pricing Data...")
        
        local_pricing = self.get_pricing_data(self.local_conn)
        vps_pricing = self.get_pricing_data(self.vps_conn)
        
        print(f"  Local pricing records: {len(local_pricing):,}")
        print(f"  VPS pricing records: {len(vps_pricing):,}")
        
        # Find parts with pricing on local but not VPS
        missing_pricing = []
        for part_num, price_data in local_pricing.items():
            if part_num not in vps_pricing:
                missing_pricing.append({
                    'part_number': part_num,
                    'local_pricing': price_data
                })
        
        self.results['missing_on_vps']['pricing'] = missing_pricing
        print(f"  ❌ Parts with missing pricing on VPS: {len(missing_pricing):,}")
        
        # Find pricing mismatches
        mismatched = []
        for part_num in local_pricing:
            if part_num in vps_pricing:
                local = local_pricing[part_num]
                vps = vps_pricing[part_num]
                
                # Check for significant price differences
                for price_type in ['list_price', 'vor_price', 'stock_order_price']:
                    local_price = local.get(price_type)
                    vps_price = vps.get(price_type)
                    
                    if local_price != vps_price:
                        mismatched.append({
                            'part_number': part_num,
                            'price_type': price_type,
                            'local_price': local_price,
                            'vps_price': vps_price
                        })
        
        self.results['mismatched_prices'] = mismatched
        print(f"  ⚠️ Price mismatches found: {len(mismatched):,}")
        
        if missing_pricing:
            print("  📋 Sample parts missing pricing on VPS:")
            for item in missing_pricing[:5]:
                print(f"    • {item['part_number']}: {item['local_pricing']}")
            if len(missing_pricing) > 5:
                print(f"    ... and {len(missing_pricing) - 5} more")

    def compare_oscar_integration(self):
        """Compare Oscar products and stock records"""
        print("\n🛒 Comparing Oscar Products & Stock...")
        
        local_products = self.get_oscar_products(self.local_conn)
        vps_products = self.get_oscar_products(self.vps_conn)
        
        print(f"  Local Oscar products: {len(local_products):,}")
        print(f"  VPS Oscar products: {len(vps_products):,}")
        
        # Find products missing on VPS
        missing_products = []
        for upc, product_data in local_products.items():
            if upc not in vps_products:
                missing_products.append({
                    'upc': upc,
                    'title': product_data['title'],
                    'local_price': product_data['price'],
                    'local_stock': product_data['stock']
                })
        
        self.results['missing_on_vps']['oscar_products'] = missing_products
        print(f"  ❌ Oscar products missing on VPS: {len(missing_products):,}")
        
        # Check for products without pricing
        no_pricing_local = [upc for upc, data in local_products.items() if data['price'] is None]
        no_pricing_vps = [upc for upc, data in vps_products.items() if data['price'] is None]
        
        print(f"  ⚠️ Local products without pricing: {len(no_pricing_local):,}")
        print(f"  ⚠️ VPS products without pricing: {len(no_pricing_vps):,}")
        
        # Check for products without stock
        no_stock_local = [upc for upc, data in local_products.items() if data['stock'] == 0]
        no_stock_vps = [upc for upc, data in vps_products.items() if data['stock'] == 0]
        
        print(f"  ⚠️ Local products without stock: {len(no_stock_local):,}")
        print(f"  ⚠️ VPS products without stock: {len(no_stock_vps):,}")

    def analyze_specific_part(self, part_number):
        """Analyze a specific part number across both databases"""
        print(f"\n🔍 Analyzing specific part: {part_number}")
        
        # Check local database
        local_cursor = self.local_conn.cursor()
        
        # Get part info
        local_cursor.execute(
            "SELECT id, usage_name FROM motorpartsdata_part WHERE part_number = %s",
            (part_number,)
        )
        local_part = local_cursor.fetchone()
        
        if local_part:
            part_id = local_part[0]
            print(f"  📦 LOCAL Part: {local_part[1]}")
            
            # Get pricing
            local_cursor.execute(
                "SELECT list_price, vor, stock_order FROM motorpartsdata_pricingdata WHERE part_number_id = %s",
                (part_id,)
            )
            local_pricing = local_cursor.fetchone()
            if local_pricing:
                print(f"  💰 LOCAL Pricing: List={local_pricing[0]}, VOR={local_pricing[1]}, Stock={local_pricing[2]}")
            else:
                print("  ❌ LOCAL: No pricing data")
            
            # Get Oscar product - search by UPC and title
            local_cursor.execute(
                """SELECT p.title, sr.price, sr.num_in_stock 
                   FROM catalogue_product p 
                   LEFT JOIN partner_stockrecord sr ON p.id = sr.product_id 
                   WHERE p.upc = %s OR p.title LIKE %s""",
                (part_number, f'%{part_number}%')
            )
            local_oscar = local_cursor.fetchone()
            if local_oscar:
                print(f"  🛒 LOCAL Oscar: {local_oscar[0][:50]}..., Price={local_oscar[1]}, Stock={local_oscar[2]}")
            else:
                print("  ❌ LOCAL: No Oscar product found")
        else:
            print("  ❌ LOCAL: Part not found")
        
        # Check VPS database
        vps_cursor = self.vps_conn.cursor()
        
        # Get part info
        vps_cursor.execute(
            "SELECT id, usage_name FROM motorpartsdata_part WHERE part_number = %s",
            (part_number,)
        )
        vps_part = vps_cursor.fetchone()
        
        if vps_part:
            part_id = vps_part[0]
            print(f"  📦 VPS Part: {vps_part[1]}")
            
            # Get pricing
            vps_cursor.execute(
                "SELECT list_price, vor, stock_order FROM motorpartsdata_pricingdata WHERE part_number_id = %s",
                (part_id,)
            )
            vps_pricing = vps_cursor.fetchone()
            if vps_pricing:
                print(f"  💰 VPS Pricing: List={vps_pricing[0]}, VOR={vps_pricing[1]}, Stock={vps_pricing[2]}")
            else:
                print("  ❌ VPS: No pricing data")
            
            # Get Oscar product - search by UPC and title
            vps_cursor.execute(
                """SELECT p.title, sr.price, sr.num_in_stock 
                   FROM catalogue_product p 
                   LEFT JOIN partner_stockrecord sr ON p.id = sr.product_id 
                   WHERE p.upc = %s OR p.title LIKE %s""",
                (part_number, f'%{part_number}%')
            )
            vps_oscar = vps_cursor.fetchone()
            if vps_oscar:
                print(f"  🛒 VPS Oscar: {vps_oscar[0][:50]}..., Price={vps_oscar[1]}, Stock={vps_oscar[2]}")
            else:
                print("  ❌ VPS: No Oscar product found")
        else:
            print("  ❌ VPS: Part not found")
        
        local_cursor.close()
        vps_cursor.close()

    def generate_recommendations(self):
        """Generate recommendations based on findings"""
        print("\n📋 RECOMMENDATIONS:")
        print("=" * 50)
        
        missing_parts = len(self.results['missing_on_vps']['parts'])
        missing_pricing = len(self.results['missing_on_vps']['pricing'])
        missing_oscar = len(self.results['missing_on_vps']['oscar_products'])
        
        if missing_parts > 0:
            print(f"1. 🔄 SYNC PARTS DATA: {missing_parts:,} parts are missing on VPS")
            print("   Run: python scrapeandpush.py (or your data sync script)")
            self.results['issues_found'].append(f"Missing {missing_parts} parts on VPS")
        
        if missing_pricing > 0:
            print(f"2. 💰 SYNC PRICING DATA: {missing_pricing:,} parts lack pricing on VPS")
            print("   Run: python loadprices.py")
            self.results['issues_found'].append(f"Missing pricing for {missing_pricing} parts on VPS")
        
        if missing_oscar > 0:
            print(f"3. 🛒 SYNC OSCAR PRODUCTS: {missing_oscar:,} Oscar products missing on VPS")
            print("   Run: python import_to_oscar.py")
            self.results['issues_found'].append(f"Missing {missing_oscar} Oscar products on VPS")
        
        if len(self.results['mismatched_prices']) > 0:
            print(f"4. ⚠️ PRICE MISMATCHES: {len(self.results['mismatched_prices']):,} price differences found")
            print("   Review and resync pricing data")
            self.results['issues_found'].append(f"Price mismatches found: {len(self.results['mismatched_prices'])}")
        
        if not self.results['issues_found']:
            print("✅ No major issues found! Databases appear to be in sync.")

    def save_detailed_report(self):
        """Save detailed findings to a JSON file"""
        report_file = 'database_comparison_report.json'
        
        # Convert results to JSON-serializable format
        json_results = {}
        for key, value in self.results.items():
            if isinstance(value, dict):
                json_results[key] = {k: v for k, v in value.items()}
            else:
                json_results[key] = value
        
        with open(report_file, 'w') as f:
            json.dump(json_results, f, indent=2, default=str)
        
        print(f"\n📄 Detailed report saved to: {report_file}")

    def run_comparison(self):
        """Run the complete database comparison"""
        print("🔍 Database Comparison Tool: Local vs VPS")
        print("=" * 50)
        
        self.connect_databases()
        
        # Get basic statistics
        print("\n📊 Database Statistics:")
        self.results['local_stats'] = self.get_table_stats(self.local_conn, "LOCAL")
        self.results['vps_stats'] = self.get_table_stats(self.vps_conn, "VPS")
        
        # Run comparisons
        self.compare_parts()
        self.compare_pricing()
        self.compare_oscar_integration()
        
        # Analyze specific parts from the JSON file if available
        sample_parts = ["C00112285"]  # From the attached JSON
        for part_num in sample_parts:
            self.analyze_specific_part(part_num)
        
        # Generate recommendations
        self.generate_recommendations()
        
        # Save detailed report
        self.save_detailed_report()
        
        # Close connections
        if self.local_conn:
            self.local_conn.close()
        if self.vps_conn:
            self.vps_conn.close()
        
        print("\n✅ Database comparison completed!")

def main():
    """Main function"""
    try:
        comparator = DatabaseComparator()
        comparator.run_comparison()
    except KeyboardInterrupt:
        print("\n⚠️ Script interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

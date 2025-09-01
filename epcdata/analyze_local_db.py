#!/usr/bin/env python3
"""
Local Database Analysis Script
=============================

This script analyzes just the local database to understand the current state
of parts, pricing, and Oscar integration before attempting VPS comparison.
"""

import psycopg2
import sys
from decimal import Decimal

# Local Database Configuration
LOCAL_DB_CONFIG = {
    'host': 'localhost',
    'database': 'vansdirect',
    'user': 'postgres',
    'password': 'letmein123',
    'port': '5432'
}

def analyze_local_database():
    """Analyze the local database comprehensively"""
    print("🔍 Local Database Analysis")
    print("=" * 40)
    
    try:
        conn = psycopg2.connect(**LOCAL_DB_CONFIG)
        cursor = conn.cursor()
        
        # 1. Check Parts
        cursor.execute("SELECT COUNT(*) FROM motorpartsdata_part")
        parts_count = cursor.fetchone()[0]
        print(f"📦 Total Parts: {parts_count:,}")
        
        # 2. Check Pricing Data
        cursor.execute("SELECT COUNT(*) FROM motorpartsdata_pricingdata")
        pricing_count = cursor.fetchone()[0]
        print(f"💰 Total Pricing Records: {pricing_count:,}")
        
        # 3. Check Oscar Products
        cursor.execute("SELECT COUNT(*) FROM catalogue_product WHERE upc IS NOT NULL")
        oscar_products = cursor.fetchone()[0]
        print(f"🛒 Oscar Products (with UPC): {oscar_products:,}")
        
        # 4. Check Stock Records
        cursor.execute("SELECT COUNT(*) FROM partner_stockrecord")
        stock_records = cursor.fetchone()[0]
        print(f"📊 Stock Records: {stock_records:,}")
        
        print("\n🔍 Detailed Analysis:")
        
        # Parts without pricing
        cursor.execute("""
            SELECT COUNT(*) 
            FROM motorpartsdata_part p 
            LEFT JOIN motorpartsdata_pricingdata pd ON p.id = pd.part_number_id 
            WHERE pd.id IS NULL
        """)
        parts_no_pricing = cursor.fetchone()[0]
        print(f"❌ Parts without pricing: {parts_no_pricing:,}")
        
        # Parts without Oscar products
        cursor.execute("""
            SELECT COUNT(*) 
            FROM motorpartsdata_part p 
            LEFT JOIN catalogue_product cp ON p.part_number = cp.upc 
            WHERE cp.id IS NULL
        """)
        parts_no_oscar = cursor.fetchone()[0]
        print(f"❌ Parts without Oscar products: {parts_no_oscar:,}")
        
        # Oscar products without stock records
        cursor.execute("""
            SELECT COUNT(*) 
            FROM catalogue_product p 
            LEFT JOIN partner_stockrecord sr ON p.id = sr.product_id 
            WHERE p.upc IS NOT NULL AND sr.id IS NULL
        """)
        oscar_no_stock = cursor.fetchone()[0]
        print(f"❌ Oscar products without stock: {oscar_no_stock:,}")
        
        # Sample parts with all data
        print(f"\n📋 Sample parts with complete data:")
        cursor.execute("""
            SELECT p.part_number, p.usage_name, pd.list_price, pd.vor, sr.num_in_stock
            FROM motorpartsdata_part p
            JOIN motorpartsdata_pricingdata pd ON p.id = pd.part_number_id
            JOIN catalogue_product cp ON p.part_number = cp.upc
            JOIN partner_stockrecord sr ON cp.id = sr.product_id
            WHERE pd.list_price IS NOT NULL AND pd.list_price != ''
            LIMIT 5
        """)
        
        complete_parts = cursor.fetchall()
        for part in complete_parts:
            print(f"  ✅ {part[0]}: {part[1]}, Price: {part[2]}, VOR: {part[3]}, Stock: {part[4]}")
        
        # Sample parts missing pricing
        print(f"\n📋 Sample parts missing pricing:")
        cursor.execute("""
            SELECT p.part_number, p.usage_name
            FROM motorpartsdata_part p 
            LEFT JOIN motorpartsdata_pricingdata pd ON p.id = pd.part_number_id 
            WHERE pd.id IS NULL
            LIMIT 5
        """)
        
        missing_pricing = cursor.fetchall()
        for part in missing_pricing:
            print(f"  ❌ {part[0]}: {part[1]} - NO PRICING")
        
        # Analyze specific part C00112285
        print(f"\n🔍 Analyzing part C00112285:")
        
        # Check if part exists
        cursor.execute("SELECT id, usage_name FROM motorpartsdata_part WHERE part_number = %s", ("C00112285",))
        part_data = cursor.fetchone()
        
        if part_data:
            part_id = part_data[0]
            print(f"  📦 Part found: {part_data[1]}")
            
            # Check pricing
            cursor.execute("SELECT list_price, vor, stock_order FROM motorpartsdata_pricingdata WHERE part_number_id = %s", (part_id,))
            pricing_data = cursor.fetchone()
            
            if pricing_data:
                print(f"  💰 Pricing: List={pricing_data[0]}, VOR={pricing_data[1]}, Stock Order={pricing_data[2]}")
            else:
                print("  ❌ No pricing data found")
            
            # Check Oscar product
            cursor.execute("SELECT title FROM catalogue_product WHERE upc = %s", ("C00112285",))
            oscar_data = cursor.fetchone()
            
            if oscar_data:
                print(f"  🛒 Oscar product: {oscar_data[0]}")
                
                # Check stock
                cursor.execute("""
                    SELECT sr.price, sr.num_in_stock 
                    FROM catalogue_product p 
                    JOIN partner_stockrecord sr ON p.id = sr.product_id 
                    WHERE p.upc = %s
                """, ("C00112285",))
                stock_data = cursor.fetchone()
                
                if stock_data:
                    print(f"  📊 Stock: Price={stock_data[0]}, Quantity={stock_data[1]}")
                else:
                    print("  ❌ No stock record found")
            else:
                print("  ❌ No Oscar product found")
        else:
            print("  ❌ Part C00112285 not found in database")
        
        cursor.close()
        conn.close()
        
        print("\n✅ Local analysis completed!")
        
    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")

if __name__ == "__main__":
    analyze_local_database()

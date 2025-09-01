#!/usr/bin/env python3
"""
Quick test of the Oscar product search for C00112285
"""

import psycopg2

# Database Configuration
LOCAL_DB_CONFIG = {
    'host': 'localhost',
    'database': 'vansdirect',
    'user': 'postgres',
    'password': 'letmein123',
    'port': '5432'
}

def test_oscar_search(part_number):
    print(f"🔍 Testing Oscar search for: {part_number}")
    
    try:
        conn = psycopg2.connect(**LOCAL_DB_CONFIG)
        cursor = conn.cursor()
        
        # Test the query
        cursor.execute(
            """SELECT p.title, sr.price, sr.num_in_stock 
               FROM catalogue_product p 
               LEFT JOIN partner_stockrecord sr ON p.id = sr.product_id 
               WHERE p.upc = %s OR p.title LIKE %s""",
            (part_number, f'%{part_number}%')
        )
        
        results = cursor.fetchall()
        print(f"Found {len(results)} results:")
        
        for result in results:
            print(f"  📦 Title: {result[0]}")
            print(f"  💰 Price: {result[1]}")
            print(f"  📊 Stock: {result[2]}")
            print("  ---")
        
        if not results:
            print("  ❌ No Oscar products found")
            
            # Let's check if there are any products at all
            cursor.execute("SELECT COUNT(*) FROM catalogue_product")
            total = cursor.fetchone()[0]
            print(f"  📊 Total Oscar products in DB: {total}")
            
            # Check sample products
            cursor.execute("SELECT upc, title FROM catalogue_product WHERE upc IS NOT NULL LIMIT 3")
            samples = cursor.fetchall()
            print("  📋 Sample products:")
            for sample in samples:
                print(f"    • {sample[0]} - {sample[1][:40]}...")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_oscar_search("C00112285")

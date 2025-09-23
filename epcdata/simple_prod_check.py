#!/usr/bin/env python
"""
Simple Production Category Check using Direct SQL
"""

import psycopg2

def check_production():
    print("🎯 SIMPLE PRODUCTION CHECK")
    print("="*30)
    
    try:
        conn = psycopg2.connect(
            host='80.95.207.42',
            database='parts_store',
            user='postgres',
            password='N0rwich!',
            port=5432
        )
        
        cursor = conn.cursor()
        
        # Test basic connection
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        print(f"✅ Connection test: {result[0]}")
        
        # Count categories
        cursor.execute("SELECT COUNT(*) FROM catalogue_category")
        count = cursor.fetchone()[0]
        print(f"✅ Total categories: {count}")
        
        # Search for our specific categories
        cursor.execute("SELECT name, slug FROM catalogue_category WHERE slug LIKE %s LIMIT 5", ('%LSFAL11A4PA157987%',))
        categories = cursor.fetchall()
        
        print(f"\\n📁 Sample categories for LSFAL11A4PA157987:")
        for cat in categories:
            print(f"  • {cat[0]} ({cat[1]})")
        
        # Look specifically for parent-12 child-1
        cursor.execute("SELECT name, slug FROM catalogue_category WHERE slug = %s", ('serial-LSFAL11A4PA157987-parent-12-child-1',))
        target_cat = cursor.fetchone()
        
        if target_cat:
            print(f"\\n🎯 Found target category:")
            print(f"  Name: {target_cat[0]}")
            print(f"  Slug: {target_cat[1]}")
            
            # Check products in this category
            cursor.execute("""
                SELECT COUNT(*) FROM catalogue_productcategory pc 
                JOIN catalogue_category c ON pc.category_id = c.id
                WHERE c.slug = %s
            """, ('serial-LSFAL11A4PA157987-parent-12-child-1',))
            
            product_count = cursor.fetchone()[0]
            print(f"  Products: {product_count}")
            
            if product_count == 0:
                print("  ❌ THIS CATEGORY IS EMPTY - THAT'S THE PROBLEM!")
        else:
            print("\\n❌ Target category not found!")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_production()
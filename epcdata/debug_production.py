#!/usr/bin/env python
"""
Debug Production Database Connection
"""

import psycopg2

def debug_production():
    print("🔍 DEBUG PRODUCTION DATABASE")
    print("="*40)
    
    conn = psycopg2.connect(
        host='80.95.207.42',
        database='parts_store', 
        user='postgres',
        password='N0rwich!',
        port=5432
    )
    
    cursor = conn.cursor()
    
    print("✅ Connected successfully")
    
    # Test basic query first
    cursor.execute("SELECT COUNT(*) FROM catalogue_category;")
    total_cats = cursor.fetchone()[0]
    print(f"Total categories: {total_cats}")
    
    # Find categories for our serial
    serial = 'LSFAL11A4PA157987'
    print(f"\\nSearching for categories with serial: {serial}")
    
    cursor.execute("""
        SELECT id, name, slug 
        FROM catalogue_category 
        WHERE slug LIKE %s 
        LIMIT 10;
    """, (f'%{serial}%',))
    
    results = cursor.fetchall()
    print(f"Found {len(results)} matching categories:")
    
    for result in results:
        print(f"  ID: {result[0]}")
        print(f"  Name: {result[1]}")
        print(f"  Slug: {result[2]}")
        print("  ---")
    
    # Check for parent-12 specifically  
    cursor.execute("""
        SELECT id, name, slug
        FROM catalogue_category 
        WHERE slug LIKE %s AND slug LIKE %s
        LIMIT 5;
    """, (f'%{serial}%', '%parent-12%'))
    
    parent12_results = cursor.fetchall()
    print(f"\\nParent-12 categories: {len(parent12_results)}")
    
    for result in parent12_results:
        print(f"  {result[1]} ({result[2]})")
        
        # Check products in this category
        cursor.execute("""
            SELECT COUNT(*) 
            FROM catalogue_productcategory 
            WHERE category_id = %s;
        """, (result[0],))
        
        count = cursor.fetchone()[0]
        print(f"    Products: {count}")
    
    cursor.close()
    conn.close()
    print("\\n✅ Analysis complete")

if __name__ == "__main__":
    debug_production()
#!/usr/bin/env python
"""
Find Energy Storage Products on Production
"""

import psycopg2

def find_energy_products():
    print("⚡ FINDING ENERGY STORAGE PRODUCTS")
    print("="*50)
    
    conn = psycopg2.connect(
        host='80.95.207.42',
        database='parts_store',
        user='postgres', 
        password='N0rwich!',
        port=5432
    )
    
    cursor = conn.cursor()
    serial = 'LSFAL11A4PA157987'
    
    # Find ALL products for this serial that contain energy keywords
    cursor.execute("""
        SELECT 
            p.title,
            c.name as category_name,
            c.slug as category_slug
        FROM catalogue_product p
        JOIN catalogue_productcategory pc ON p.id = pc.product_id  
        JOIN catalogue_category c ON pc.category_id = c.id
        WHERE c.slug LIKE %s
        AND (
            UPPER(p.title) LIKE '%BATTERY%' OR
            UPPER(p.title) LIKE '%ENERGY%' OR  
            UPPER(p.title) LIKE '%POWER%' OR
            UPPER(p.title) LIKE '%ELECTRICAL%' OR
            UPPER(p.title) LIKE '%TRAY%' OR
            UPPER(p.title) LIKE '%INTELLIGENT%' OR
            UPPER(p.title) LIKE '%BOARD%' OR
            UPPER(p.title) LIKE '%ASSEMBLY%'
        )
        ORDER BY c.slug;
    """, (f'%{serial}%',))
    
    products = cursor.fetchall()
    print(f"Found {len(products)} energy storage products:")
    print()
    
    # Group by parent
    by_parent = {}
    
    for product in products:
        row = product
        title = row[0]
        cat_name = row[1]  
        cat_slug = row[2]
        print(f"⚡ {title}")
        print(f"   Category: {cat_name}")
        print(f"   Slug: {cat_slug}")
        
        # Extract parent number
        parts = cat_slug.split('-')
        parent_num = 'unknown'
        for i, part in enumerate(parts):
            if part == 'parent' and i + 1 < len(parts):
                parent_num = parts[i + 1]
                break
        
        print(f"   Parent: {parent_num}")
        print()
        
        if parent_num not in by_parent:
            by_parent[parent_num] = []
        by_parent[parent_num].append(title)
    
    print("📊 SUMMARY BY PARENT:")
    for parent in sorted(by_parent.keys()):
        prods = by_parent[parent]
        print(f"  Parent-{parent}: {len(prods)} products")
        for prod in prods:
            print(f"    • {prod}")
    
    # Check what should be in parent-2 (energy storage)
    print("\\n🎯 CHECKING PARENT-2 CATEGORIES:")
    cursor.execute("""
        SELECT c.name, c.slug, COUNT(pc.product_id) as product_count
        FROM catalogue_category c
        LEFT JOIN catalogue_productcategory pc ON c.id = pc.category_id
        WHERE c.slug LIKE %s AND c.slug LIKE '%parent-2%'
        GROUP BY c.id, c.name, c.slug;
    """, (f'%{serial}%',))
    
    parent2_cats = cursor.fetchall()
    for cat in parent2_cats:
        row = cat
        name = row[0]
        slug = row[1] 
        count = row[2]
        print(f"  📁 {name} ({slug}) - {count} products")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    find_energy_products()
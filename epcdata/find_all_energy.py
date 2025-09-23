#!/usr/bin/env python
"""
Find where energy storage products actually are
"""

import psycopg2

conn = psycopg2.connect(
    host='80.95.207.42',
    database='parts_store',
    user='postgres',
    password='N0rwich!',
    port=5432
)

cursor = conn.cursor()
serial = 'LSFAL11A4PA157987'

print("⚡ FINDING ENERGY STORAGE PRODUCTS")
print("="*40)

# Find products with energy-related keywords
energy_keywords = ['BATTERY', 'ENERGY', 'POWER', 'ELECTRICAL', 'TRAY']

all_energy_products = []

for keyword in energy_keywords:
    print(f"\\n🔍 Searching for '{keyword}' products...")
    
    cursor.execute("""
        SELECT p.title, c.name, c.slug
        FROM catalogue_product p
        JOIN catalogue_productcategory pc ON p.id = pc.product_id
        JOIN catalogue_category c ON pc.category_id = c.id
        WHERE c.slug LIKE %s AND UPPER(p.title) LIKE %s
    """, (f'%{serial}%', f'%{keyword}%'))
    
    keyword_products = cursor.fetchall()
    print(f"  Found {len(keyword_products)} products with '{keyword}':")
    
    for product in keyword_products:
        title, cat_name, cat_slug = product
        print(f"    • {title}")
        print(f"      Category: {cat_name}")
        print(f"      Slug: {cat_slug}")
        
        # Extract parent number
        parts = cat_slug.split('-')
        parent_num = 'unknown'
        for i, part in enumerate(parts):
            if part == 'parent' and i + 1 < len(parts):
                parent_num = parts[i + 1]
                break
        
        print(f"      Parent: {parent_num}")
        print()
        
        all_energy_products.append((title, cat_name, cat_slug, parent_num))

# Summary by parent
print("\\n📊 SUMMARY BY PARENT CATEGORY:")
by_parent = {}
for title, cat_name, cat_slug, parent_num in all_energy_products:
    if parent_num not in by_parent:
        by_parent[parent_num] = []
    by_parent[parent_num].append(title)

for parent in sorted(by_parent.keys()):
    products = by_parent[parent]
    print(f"\\n🏷️  Parent-{parent}: {len(products)} products")
    for product in products:
        print(f"   • {product}")

# Check what should be in parent-2 (energy storage target)
print("\\n\\n🎯 CHECKING PARENT-2 CATEGORIES (WHERE ENERGY SHOULD BE):")
cursor.execute("""
    SELECT c.name, c.slug, 
           (SELECT COUNT(*) FROM catalogue_productcategory pc WHERE pc.category_id = c.id) as product_count
    FROM catalogue_category c 
    WHERE c.slug LIKE %s AND c.slug LIKE %s
""", (f'%{serial}%', '%parent-2%'))

parent2_categories = cursor.fetchall()
for cat in parent2_categories:
    name, slug, count = cat
    print(f"  📁 {name}")
    print(f"     Slug: {slug}")
    print(f"     Products: {count}")

cursor.close()
conn.close()

print("\\n✅ Analysis complete!")
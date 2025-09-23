#!/usr/bin/env python
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

print("🔍 SEARCHING FOR ENERGY STORAGE PRODUCTS")
print("="*50)

# Simple query for products with BATTERY in the title
cursor.execute("""
    SELECT p.title, c.name, c.slug
    FROM catalogue_product p
    JOIN catalogue_productcategory pc ON p.id = pc.product_id
    JOIN catalogue_category c ON pc.category_id = c.id  
    WHERE c.slug LIKE %s AND UPPER(p.title) LIKE '%BATTERY%'
    ORDER BY p.title;
""", (f'%{serial}%',))

battery_products = cursor.fetchall()
print(f"Found {len(battery_products)} products with 'BATTERY' in title:")

for i, row in enumerate(battery_products):
    print(f"{i+1}. {row[0]}")
    print(f"   Category: {row[1]}")
    print(f"   Slug: {row[2]}")
    print()

cursor.close()
conn.close()
#!/usr/bin/env python3
"""
Check what happened with the production import - why no products are showing
Connects directly to production PostgreSQL database
"""
import psycopg2
from psycopg2.extras import RealDictCursor

def main():
    print('🔍 PRODUCTION DATABASE DIAGNOSTIC')
    print('=' * 60)
    
    # Production database connection
    try:
        conn = psycopg2.connect(
            host="80.95.207.42",
            database="parts_store", 
            user="postgres",
            password="N0rwich!",
            cursor_factory=RealDictCursor
        )
        cur = conn.cursor()
        print('✅ Connected to production database')
        
        # Check Django models first
        print('\n🗄️ DJANGO MODELS CHECK')
        print('=' * 30)
        
        # Check SerialNumber
        cur.execute("SELECT * FROM motorpartsdata_serialnumber WHERE serial_number = 'LSFAL11A4PA157987'")
        serial = cur.fetchone()
        if serial:
            print(f"📋 Django Serial: {serial['serial_number']} - {serial['brand_name']}")
            
            # Check ParentTitles
            cur.execute("SELECT COUNT(*) as count FROM motorpartsdata_parenttitle WHERE serial_number_id = %s", (serial['id'],))
            parent_count = cur.fetchone()['count']
            print(f"📁 Django Parents: {parent_count}")
            
            # Check ChildTitles
            cur.execute("""
                SELECT COUNT(*) as count FROM motorpartsdata_childtitle ct 
                JOIN motorpartsdata_parenttitle pt ON ct.parent_title_id = pt.id 
                WHERE pt.serial_number_id = %s
            """, (serial['id'],))
            child_count = cur.fetchone()['count']
            print(f"📂 Django Children: {child_count}")
            
            # Check Parts
            cur.execute("SELECT COUNT(*) as count FROM motorpartsdata_part WHERE serial_number_id = %s", (serial['id'],))
            part_count = cur.fetchone()['count']
            print(f"🔧 Django Parts: {part_count}")
            
            # Sample parts
            cur.execute("""
                SELECT p.part_number, ct.title as child_title, pt.title as parent_title 
                FROM motorpartsdata_part p 
                JOIN motorpartsdata_childtitle ct ON p.child_title_id = ct.id
                JOIN motorpartsdata_parenttitle pt ON ct.parent_title_id = pt.id
                WHERE p.serial_number_id = %s 
                LIMIT 3
            """, (serial['id'],))
            sample_parts = cur.fetchall()
            for part in sample_parts:
                print(f"   Sample: {part['part_number']} -> {part['child_title']} (Parent: {part['parent_title']})")
        else:
            print('❌ No Django serial found in production')
        
        # Check Oscar categories
        print('\n🛒 OSCAR CATALOGUE CHECK')
        print('=' * 30)
        
        # Look for the serial category
        cur.execute("SELECT * FROM catalogue_category WHERE name ILIKE '%lsfal11a4pa157987%'")
        serial_cats = cur.fetchall()
        print(f"📁 Oscar Serial Categories: {len(serial_cats)}")
        
        for cat in serial_cats:
            # Count products in this category
            cur.execute("""
                SELECT COUNT(*) as count FROM catalogue_productcategory pc 
                WHERE pc.category_id = %s
            """, (cat['id'],))
            product_count = cur.fetchone()['count']
            print(f"   • {cat['name']} (ID: {cat['id']}, slug: {cat['slug']}) - {product_count} products")
            
            # Check children categories
            cur.execute("SELECT * FROM catalogue_category WHERE path LIKE %s AND id != %s", (f"{cat['path']}%", cat['id']))
            children = cur.fetchall()
            print(f"     Has {len(children)} child categories")
            
            for child in children[:3]:  # Show first 3
                cur.execute("""
                    SELECT COUNT(*) as count FROM catalogue_productcategory pc 
                    WHERE pc.category_id = %s
                """, (child['id'],))
                child_product_count = cur.fetchone()['count']
                print(f"       └─ {child['name']} (ID: {child['id']}) - {child_product_count} products")
        
        # Check all Oscar products for this serial
        cur.execute("""
            SELECT COUNT(*) as count FROM catalogue_product p 
            JOIN catalogue_productcategory pc ON p.id = pc.product_id 
            JOIN catalogue_category c ON pc.category_id = c.id 
            WHERE c.name ILIKE '%lsfal11a4pa157987%'
        """)
        total_products = cur.fetchone()['count']
        print(f"\n📦 Total Oscar Products for serial: {total_products}")
        
        # If we have categories but no products, investigate further
        if serial_cats and total_products == 0:
            print('\n⚠️  ISSUE DETECTED: Categories exist but no products!')
            print('This suggests the import created the category structure but failed to assign products.')
            
            # Check if products exist but aren't properly categorized
            cur.execute("SELECT * FROM catalogue_product WHERE title ILIKE '%LSFAL11A4PA157987%' LIMIT 5")
            orphan_products = cur.fetchall()
            print(f"🔍 Products with LSFAL11A4PA157987 in title: {len(orphan_products)}")
            
            for product in orphan_products:
                cur.execute("""
                    SELECT c.name FROM catalogue_category c 
                    JOIN catalogue_productcategory pc ON c.id = pc.category_id 
                    WHERE pc.product_id = %s
                """, (product['id'],))
                categories = cur.fetchall()
                cat_names = [c['name'] for c in categories]
                print(f"   • {product['title']} - Categories: {cat_names}")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")

if __name__ == '__main__':
    main()
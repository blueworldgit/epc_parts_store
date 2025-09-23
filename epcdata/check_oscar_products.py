#!/usr/bin/env python3
"""
Check for Oscar products that should belong to LSFAL11A4PA157987 but might be orphaned
"""
import psycopg2
from psycopg2.extras import RealDictCursor

def main():
    print('🔍 OSCAR PRODUCT ORPHAN INVESTIGATION')
    print('=' * 60)
    
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
        
        # Check total Oscar products
        print('\n📊 OSCAR PRODUCT OVERVIEW')
        print('=' * 25)
        
        cur.execute("SELECT COUNT(*) as total FROM catalogue_product")
        total_products = cur.fetchone()['total']
        print(f"📦 Total Oscar products: {total_products}")
        
        # Look for products that might belong to LSFAL but aren't in LSFAL categories
        print('\n🔍 SEARCHING FOR LSFAL-RELATED PRODUCTS')
        print('=' * 40)
        
        # Search by UPC (which might contain part numbers from Django)
        cur.execute("""
            SELECT p.id, p.title, p.upc, COUNT(pc.category_id) as category_count
            FROM catalogue_product p
            LEFT JOIN catalogue_productcategory pc ON p.id = pc.product_id
            WHERE p.upc IN (
                SELECT DISTINCT part_number FROM motorpartsdata_part mp
                JOIN motorpartsdata_childtitle ct ON mp.child_title_id = ct.id
                JOIN motorpartsdata_parenttitle pt ON ct.parent_id = pt.id
                WHERE pt.serial_number_id = 1
            )
            GROUP BY p.id, p.title, p.upc
            LIMIT 10
        """)
        
        matching_products = cur.fetchall()
        print(f"📦 Products matching LSFAL part numbers: {len(matching_products)}")
        
        if matching_products:
            print("Sample matching products:")
            for product in matching_products:
                print(f"   • {product['title']} (UPC: {product['upc']}, {product['category_count']} categories)")
                
                # Check which categories these products are in
                cur.execute("""
                    SELECT c.name, c.slug, c.depth 
                    FROM catalogue_category c
                    JOIN catalogue_productcategory pc ON c.id = pc.category_id
                    WHERE pc.product_id = %s
                    ORDER BY c.depth
                """, (product['id'],))
                product_cats = cur.fetchall()
                
                for cat in product_cats:
                    indent = "     " + ("  " * cat['depth'])
                    print(f"{indent}└─ {cat['name']} (depth: {cat['depth']})")
        
        # Check Django vs Oscar product count mismatch
        print('\n📊 IMPORT VERIFICATION')
        print('=' * 20)
        
        # Count Django parts that should be imported
        cur.execute("""
            SELECT COUNT(*) as django_parts FROM motorpartsdata_part mp
            JOIN motorpartsdata_childtitle ct ON mp.child_title_id = ct.id
            JOIN motorpartsdata_parenttitle pt ON ct.parent_id = pt.id
            WHERE pt.serial_number_id = 1
        """)
        django_count = cur.fetchone()['django_parts']
        
        # Count Oscar products with matching UPCs
        cur.execute("""
            SELECT COUNT(*) as oscar_products FROM catalogue_product p
            WHERE p.upc IN (
                SELECT DISTINCT part_number FROM motorpartsdata_part mp
                JOIN motorpartsdata_childtitle ct ON mp.child_title_id = ct.id
                JOIN motorpartsdata_parenttitle pt ON ct.parent_id = pt.id
                WHERE pt.serial_number_id = 1
            )
        """)
        oscar_count = cur.fetchone()['oscar_products']
        
        print(f"📋 Django parts for LSFAL: {django_count}")
        print(f"📦 Oscar products with matching UPCs: {oscar_count}")
        print(f"📊 Import success rate: {(oscar_count/django_count*100):.1f}%" if django_count > 0 else "N/A")
        
        if oscar_count == 0:
            print("❌ CRITICAL: NO Oscar products created despite Django parts being marked as imported!")
            print("   This suggests the import process has a serious bug.")
        elif oscar_count < django_count:
            print(f"⚠️  PARTIAL IMPORT: {django_count - oscar_count} products missing")
        else:
            print("✅ All Django parts have corresponding Oscar products")
        
        # Check recent import activity
        print('\n📅 RECENT IMPORT ACTIVITY')
        print('=' * 25)
        
        cur.execute("""
            SELECT DATE(oscar_imported_at) as import_date, COUNT(*) as parts_imported
            FROM motorpartsdata_part mp
            JOIN motorpartsdata_childtitle ct ON mp.child_title_id = ct.id
            JOIN motorpartsdata_parenttitle pt ON ct.parent_id = pt.id
            WHERE pt.serial_number_id = 1 AND oscar_imported_at IS NOT NULL
            GROUP BY DATE(oscar_imported_at)
            ORDER BY import_date DESC
            LIMIT 5
        """)
        
        import_activity = cur.fetchall()
        if import_activity:
            print("Recent import dates:")
            for activity in import_activity:
                print(f"   • {activity['import_date']}: {activity['parts_imported']} parts")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Database error: {e}")

if __name__ == '__main__':
    main()
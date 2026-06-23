#!/usr/bin/env python3
"""
Oscar catalogue cleanup script for LSH14C4C5NA129710
Removes ALL Oscar catalogue data for this serial
"""
import psycopg2
from psycopg2.extras import DictCursor
import sys

def main():
    serial_number = 'LSH14C4C5NA129710'
    
    print(f'🛒 OSCAR CATALOGUE CLEANUP FOR {serial_number}')
    print('=' * 60)
    
    # Production database connection
    conn = psycopg2.connect(
        host='80.95.207.42',
        database='parts_store',
        user='postgres',
        password='N0rwich!',
        port=5432
    )
    
    cur = conn.cursor(cursor_factory=DictCursor)
    
    try:
        # Start transaction
        conn.autocommit = False
        
        print(f'🔍 Finding Oscar data for {serial_number}...')
        
        # Check what Oscar tables exist first
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name LIKE 'catalogue_%'
            ORDER BY table_name
        """)
        oscar_tables = cur.fetchall()
        print(f'📊 Found Oscar tables: {[t["table_name"] for t in oscar_tables]}')
        
        # Find categories related to this serial
        cur.execute("""
            SELECT id, name, slug, depth
            FROM catalogue_category 
            WHERE name ILIKE %s OR slug ILIKE %s
            ORDER BY depth DESC
        """, (f'%{serial_number.lower()}%', f'%{serial_number.lower()}%'))
        categories = cur.fetchall()
        
        print(f'📁 Found {len(categories)} Oscar categories for {serial_number}')
        for cat in categories[:5]:  # Show first 5
            print(f'   • {cat["name"]} (depth: {cat["depth"]}, slug: {cat["slug"]})')
        
        if not categories:
            print('✅ No Oscar categories to clean up')
            return
        
        category_ids = [cat['id'] for cat in categories]
        
        # Find products related to these categories
        cur.execute("""
            SELECT COUNT(*) as product_count
            FROM catalogue_product p
            WHERE p.categories && %s
        """, (category_ids,))
        product_count = cur.fetchone()['product_count']
        
        print(f'📦 Found {product_count} Oscar products for {serial_number}')
        
        print('\n🗑️ Cleaning Oscar catalogue data...')
        
        # Delete stock records for products in these categories
        cur.execute("""
            DELETE FROM partner_stockrecord 
            WHERE product_id IN (
                SELECT p.id FROM catalogue_product p
                WHERE p.categories && %s
            )
        """, (category_ids,))
        deleted_stock = cur.rowcount
        print(f'   Deleted {deleted_stock} stock records')
        
        # Delete product attribute values
        cur.execute("""
            DELETE FROM catalogue_productattributevalue 
            WHERE product_id IN (
                SELECT p.id FROM catalogue_product p
                WHERE p.categories && %s
            )
        """, (category_ids,))
        deleted_attrs = cur.rowcount
        print(f'   Deleted {deleted_attrs} product attributes')
        
        # Delete basket line items (if any exist)
        try:
            cur.execute("""
                DELETE FROM basket_line 
                WHERE product_id IN (
                    SELECT p.id FROM catalogue_product p
                    WHERE p.categories && %s
                )
            """, (category_ids,))
            deleted_basket = cur.rowcount
            print(f'   Deleted {deleted_basket} basket line items')
        except Exception as e:
            print(f'   Skipped basket_line (table might not exist): {e}')
        
        # Delete analytics records (if table exists)
        try:
            cur.execute("""
                DELETE FROM analytics_productrecord 
                WHERE product_id IN (
                    SELECT p.id FROM catalogue_product p
                    WHERE p.categories && %s
                )
            """, (category_ids,))
            deleted_analytics = cur.rowcount
            print(f'   Deleted {deleted_analytics} analytics records')
        except Exception as e:
            print(f'   Skipped analytics_productrecord (table might not exist): {e}')
        
        # Delete products
        cur.execute("""
            DELETE FROM catalogue_product 
            WHERE categories && %s
        """, (category_ids,))
        deleted_products = cur.rowcount
        print(f'   Deleted {deleted_products} Oscar products')
        
        # Delete categories (in reverse depth order to handle hierarchy)
        for cat in categories:  # Already ordered by depth DESC
            cur.execute("""
                DELETE FROM catalogue_category 
                WHERE id = %s
            """, (cat['id'],))
            print(f'   Deleted category: {cat["name"]} (depth: {cat["depth"]})')
        
        deleted_categories = len(categories)
        
        # Commit transaction
        conn.commit()
        
        print('\n✅ OSCAR CLEANUP COMPLETED SUCCESSFULLY!')
        print(f'📊 Summary: {deleted_products} products, {deleted_categories} categories')
        print(f'🔄 Serial {serial_number} Oscar catalogue is now clean!')
        
    except Exception as e:
        # Rollback on error
        conn.rollback()
        print(f'\n❌ ERROR: {str(e)}')
        print('🔄 All changes have been rolled back')
        
        # Print detailed error for debugging
        import traceback
        traceback.print_exc()
        sys.exit(1)
        
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    main()
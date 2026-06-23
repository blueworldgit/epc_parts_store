#!/usr/bin/env python3
"""
Complete cleanup script for LSH14C4C5NA129710 serial data
Removes ALL data from both Django models AND Oscar catalogue
"""
import psycopg2
from psycopg2.extras import DictCursor
import sys

def main():
    serial_number = 'LSH14C4C5NA129710'
    
    print(f'🗑️ COMPLETE CLEANUP FOR {serial_number}')
    print('=' * 60)
    print('⚠️  WARNING: This will permanently delete ALL data for this serial!')
    print('   - Django models: SerialNumber, ParentTitle, ChildTitle, Part')
    print('   - Oscar catalogue: Products, Categories, StockRecords')
    print('   - Related pricing and analytics data')
    
    # Auto-confirm for automated execution
    print('\n✅ Proceeding with deletion...')
    
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
        
        print(f'\n🔍 Finding serial {serial_number}...')
        
        # Get serial ID
        cur.execute("""
            SELECT id FROM motorpartsdata_serialnumber 
            WHERE serial = %s
        """, (serial_number,))
        
        serial_data = cur.fetchone()
        if not serial_data:
            print(f'❌ Serial {serial_number} not found in database')
            return
        
        serial_id = serial_data['id']
        print(f'📋 Found serial ID: {serial_id}')
        
        # Get counts before deletion
        cur.execute("""
            SELECT 
                (SELECT COUNT(*) FROM motorpartsdata_parenttitle WHERE serial_number_id = %s) as parents,
                (SELECT COUNT(*) FROM motorpartsdata_childtitle ct 
                 JOIN motorpartsdata_parenttitle pt ON ct.parent_id = pt.id 
                 WHERE pt.serial_number_id = %s) as children,
                (SELECT COUNT(*) FROM motorpartsdata_part p
                 JOIN motorpartsdata_childtitle ct ON p.child_title_id = ct.id
                 JOIN motorpartsdata_parenttitle pt ON ct.parent_id = pt.id
                 WHERE pt.serial_number_id = %s) as parts
        """, (serial_id, serial_id, serial_id))
        
        counts = cur.fetchone()
        print(f'📊 Current data: {counts["parents"]} parents, {counts["children"]} children, {counts["parts"]} parts')
        
        # Check Oscar data
        cur.execute("""
            SELECT COUNT(*) as oscar_categories
            FROM catalogue_category 
            WHERE name ILIKE %s
        """, (f'%{serial_number.lower()}%',))
        oscar_cats = cur.fetchone()['oscar_categories']
        
        cur.execute("""
            SELECT COUNT(*) as oscar_products
            FROM catalogue_product p
            JOIN catalogue_product_categories pc ON p.id = pc.product_id
            JOIN catalogue_category c ON pc.category_id = c.id
            WHERE c.name ILIKE %s
        """, (f'%{serial_number.lower()}%',))
        oscar_products = cur.fetchone()['oscar_products']
        
        print(f'📊 Oscar data: {oscar_cats} categories, {oscar_products} products')
        
        if counts['parts'] == 0 and oscar_products == 0:
            print('✅ No data to clean up')
            return
        
        # STEP 1: Delete Oscar data first (due to foreign key constraints)
        print('\n🗑️ STEP 1: Cleaning Oscar catalogue data...')
        
        # Delete stock records for products related to this serial
        cur.execute("""
            DELETE FROM partner_stockrecord 
            WHERE product_id IN (
                SELECT p.id
                FROM catalogue_product p
                JOIN catalogue_product_categories pc ON p.id = pc.product_id
                JOIN catalogue_category c ON pc.category_id = c.id
                WHERE c.name ILIKE %s
            )
        """, (f'%{serial_number.lower()}%',))
        deleted_stock = cur.rowcount
        print(f'   Deleted {deleted_stock} stock records')
        
        # Delete product attribute values
        cur.execute("""
            DELETE FROM catalogue_productattributevalue 
            WHERE product_id IN (
                SELECT p.id
                FROM catalogue_product p
                JOIN catalogue_product_categories pc ON p.id = pc.product_id
                JOIN catalogue_category c ON pc.category_id = c.id
                WHERE c.name ILIKE %s
            )
        """, (f'%{serial_number.lower()}%',))
        deleted_attrs = cur.rowcount
        print(f'   Deleted {deleted_attrs} product attributes')
        
        # Delete product category relationships
        cur.execute("""
            DELETE FROM catalogue_product_categories 
            WHERE category_id IN (
                SELECT id FROM catalogue_category 
                WHERE name ILIKE %s
            )
        """, (f'%{serial_number.lower()}%',))
        deleted_cat_rels = cur.rowcount
        print(f'   Deleted {deleted_cat_rels} product-category relationships')
        
        # Delete basket line items (if any)
        cur.execute("""
            DELETE FROM basket_line 
            WHERE product_id IN (
                SELECT p.id
                FROM catalogue_product p
                JOIN catalogue_product_categories pc ON p.id = pc.product_id
                JOIN catalogue_category c ON pc.category_id = c.id
                WHERE c.name ILIKE %s
            )
        """, (f'%{serial_number.lower()}%',))
        deleted_basket = cur.rowcount
        print(f'   Deleted {deleted_basket} basket line items')
        
        # Delete analytics records
        cur.execute("""
            DELETE FROM analytics_productrecord 
            WHERE product_id IN (
                SELECT p.id
                FROM catalogue_product p
                JOIN catalogue_product_categories pc ON p.id = pc.product_id
                JOIN catalogue_category c ON pc.category_id = c.id
                WHERE c.name ILIKE %s
            )
        """, (f'%{serial_number.lower()}%',))
        deleted_analytics = cur.rowcount
        print(f'   Deleted {deleted_analytics} analytics records')
        
        # Delete products
        cur.execute("""
            DELETE FROM catalogue_product 
            WHERE id IN (
                SELECT p.id
                FROM catalogue_product p
                JOIN catalogue_product_categories pc ON p.id = pc.product_id
                JOIN catalogue_category c ON pc.category_id = c.id
                WHERE c.name ILIKE %s
            )
        """, (f'%{serial_number.lower()}%',))
        deleted_products = cur.rowcount
        print(f'   Deleted {deleted_products} Oscar products')
        
        # Delete categories (in reverse depth order to handle hierarchy)
        cur.execute("""
            DELETE FROM catalogue_category 
            WHERE name ILIKE %s
            ORDER BY depth DESC
        """, (f'%{serial_number.lower()}%',))
        deleted_categories = cur.rowcount
        print(f'   Deleted {deleted_categories} Oscar categories')
        
        # STEP 2: Delete Django models data
        print('\n🗑️ STEP 2: Cleaning Django models data...')
        
        # Delete pricing data first
        cur.execute("""
            DELETE FROM motorpartsdata_pricingdata 
            WHERE part_number_id IN (
                SELECT p.id FROM motorpartsdata_part p
                JOIN motorpartsdata_childtitle ct ON p.child_title_id = ct.id
                JOIN motorpartsdata_parenttitle pt ON ct.parent_id = pt.id
                WHERE pt.serial_number_id = %s
            )
        """, (serial_id,))
        deleted_pricing = cur.rowcount
        print(f'   Deleted {deleted_pricing} pricing records')
        
        # Delete parts
        cur.execute("""
            DELETE FROM motorpartsdata_part 
            WHERE child_title_id IN (
                SELECT ct.id FROM motorpartsdata_childtitle ct
                JOIN motorpartsdata_parenttitle pt ON ct.parent_id = pt.id
                WHERE pt.serial_number_id = %s
            )
        """, (serial_id,))
        deleted_parts = cur.rowcount
        print(f'   Deleted {deleted_parts} parts')
        
        # Delete child titles
        cur.execute("""
            DELETE FROM motorpartsdata_childtitle 
            WHERE parent_id IN (
                SELECT id FROM motorpartsdata_parenttitle 
                WHERE serial_number_id = %s
            )
        """, (serial_id,))
        deleted_children = cur.rowcount
        print(f'   Deleted {deleted_children} child titles')
        
        # Delete parent titles
        cur.execute("""
            DELETE FROM motorpartsdata_parenttitle 
            WHERE serial_number_id = %s
        """, (serial_id,))
        deleted_parents = cur.rowcount
        print(f'   Deleted {deleted_parents} parent titles')
        
        # Finally delete the serial itself
        cur.execute("""
            DELETE FROM motorpartsdata_serialnumber 
            WHERE id = %s
        """, (serial_id,))
        deleted_serial = cur.rowcount
        print(f'   Deleted {deleted_serial} serial record')
        
        # Commit transaction
        conn.commit()
        
        print('\n✅ CLEANUP COMPLETED SUCCESSFULLY!')
        print(f'📊 Summary:')
        print(f'   Django: {deleted_parts} parts, {deleted_children} children, {deleted_parents} parents, {deleted_serial} serial')
        print(f'   Oscar: {deleted_products} products, {deleted_categories} categories')
        print(f'   Related: {deleted_stock} stock, {deleted_attrs} attributes, {deleted_pricing} pricing')
        print(f'\n🔄 Serial {serial_number} is now ready for fresh import!')
        
    except Exception as e:
        # Rollback on error
        conn.rollback()
        print(f'\n❌ ERROR: {str(e)}')
        print('🔄 All changes have been rolled back')
        sys.exit(1)
        
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    main()
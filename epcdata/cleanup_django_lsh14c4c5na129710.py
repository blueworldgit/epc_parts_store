#!/usr/bin/env python3
"""
Simple cleanup script for LSH14C4C5NA129710 Django models only
Removes ALL Django motorpartsdata for this serial
"""
import psycopg2
from psycopg2.extras import DictCursor
import sys

def main():
    serial_number = 'LSH14C4C5NA129710'
    
    print(f'🗑️ DJANGO MODEL CLEANUP FOR {serial_number}')
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
        
        print(f'🔍 Finding serial {serial_number}...')
        
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
        
        if counts['parts'] == 0:
            print('✅ No data to clean up')
            return
        
        print('\n🗑️ Cleaning Django models data...')
        
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
        
        print('\n✅ DJANGO CLEANUP COMPLETED SUCCESSFULLY!')
        print(f'📊 Summary: {deleted_parts} parts, {deleted_children} children, {deleted_parents} parents, {deleted_serial} serial')
        print(f'🔄 Serial {serial_number} Django models are now clean!')
        print('\nNext steps:')
        print(f'1. python scrapeandpush.py ./LSH14C4C5NA129710')
        print(f'2. python manage.py import_to_oscar --serial LSH14C4C5NA129710')
        
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
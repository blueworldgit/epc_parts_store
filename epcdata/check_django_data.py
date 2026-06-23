#!/usr/bin/env python3
"""
Check if LSH14J7C0SA082498 data was properly loaded into Django models
"""
import psycopg2
from psycopg2.extras import DictCursor

def main():
    # Production database connection
    conn = psycopg2.connect(
        host='80.95.207.42',
        database='parts_store',
        user='postgres',
        password='N0rwich!',
        port=5432
    )
    
    cur = conn.cursor(cursor_factory=DictCursor)
    
    serial_number = 'LSH14J7C0SA082498'
    
    print(f'🔍 CHECKING DJANGO MODEL DATA FOR {serial_number}')
    print('=' * 60)
    
    # Check if serial exists
    cur.execute("""
        SELECT id, serial, vehicle_brand 
        FROM motorpartsdata_serialnumber 
        WHERE serial = %s
    """, (serial_number,))
    serial_data = cur.fetchone()
    
    if not serial_data:
        print(f'❌ Serial {serial_number} not found in database')
        return
    
    serial_id = serial_data['id']
    print(f'📋 Serial Found: {serial_data["serial"]} - {serial_data["vehicle_brand"]} (ID: {serial_id})')
    
    # Check parent titles
    cur.execute("""
        SELECT id, title 
        FROM motorpartsdata_parenttitle 
        WHERE serial_number_id = %s
        ORDER BY title
    """, (serial_id,))
    parents = cur.fetchall()
    
    print(f'\n📁 Parent Titles: {len(parents)}')
    if parents:
        for parent in parents[:10]:  # Show first 10
            print(f'   • {parent["title"]} (ID: {parent["id"]})')
        if len(parents) > 10:
            print(f'   ... and {len(parents) - 10} more')
    else:
        print('   ❌ No parent titles found')
    
    # Check child titles
    cur.execute("""
        SELECT COUNT(*) as count
        FROM motorpartsdata_childtitle ct
        JOIN motorpartsdata_parenttitle pt ON ct.parent_id = pt.id
        WHERE pt.serial_number_id = %s
    """, (serial_id,))
    child_count = cur.fetchone()['count']
    
    print(f'\n📂 Child Titles: {child_count}')
    
    if child_count > 0:
        # Show sample child titles
        cur.execute("""
            SELECT ct.id, ct.title, pt.title as parent_title
            FROM motorpartsdata_childtitle ct
            JOIN motorpartsdata_parenttitle pt ON ct.parent_id = pt.id
            WHERE pt.serial_number_id = %s
            ORDER BY pt.title, ct.title
            LIMIT 5
        """, (serial_id,))
        sample_children = cur.fetchall()
        
        for child in sample_children:
            print(f'   • {child["title"]} (Parent: {child["parent_title"]})')
        
        if child_count > 5:
            print(f'   ... and {child_count - 5} more')
    else:
        print('   ❌ No child titles found')
    
    # Check parts
    cur.execute("""
        SELECT COUNT(*) as count
        FROM motorpartsdata_part p
        JOIN motorpartsdata_childtitle ct ON p.child_title_id = ct.id
        JOIN motorpartsdata_parenttitle pt ON ct.parent_id = pt.id
        WHERE pt.serial_number_id = %s
    """, (serial_id,))
    parts_count = cur.fetchone()['count']
    
    print(f'\n🔧 Parts: {parts_count}')
    
    if parts_count > 0:
        # Show sample parts
        cur.execute("""
            SELECT p.part_number, p.usage_name, ct.title as child_title, pt.title as parent_title
            FROM motorpartsdata_part p
            JOIN motorpartsdata_childtitle ct ON p.child_title_id = ct.id
            JOIN motorpartsdata_parenttitle pt ON ct.parent_id = pt.id
            WHERE pt.serial_number_id = %s
            ORDER BY pt.title, ct.title, p.call_out_order
            LIMIT 5
        """, (serial_id,))
        sample_parts = cur.fetchall()
        
        for part in sample_parts:
            print(f'   • {part["part_number"]} - {part["usage_name"]}')
            print(f'     └─ {part["parent_title"]} → {part["child_title"]}')
        
        if parts_count > 5:
            print(f'   ... and {parts_count - 5} more')
    else:
        print('   ❌ No parts found')
    
    # Summary
    print(f'\n📊 SUMMARY FOR {serial_number}:')
    print(f'   Parents: {len(parents)}')
    print(f'   Children: {child_count}')  
    print(f'   Parts: {parts_count}')
    
    if len(parents) == 0 and child_count == 0 and parts_count == 0:
        print('\n⚠️  ISSUE: Serial exists but no data was loaded!')
        print('   This explains why scrapeandpush.py completed so quickly.')
        print('   The script may not have found HTML files in the directory structure.')
    elif parts_count == 0:
        print('\n⚠️  PARTIAL DATA: Categories exist but no parts loaded!')
    else:
        print('\n✅ Data appears to be loaded correctly')
    
    # Close connection
    cur.close()
    conn.close()

if __name__ == '__main__':
    main()
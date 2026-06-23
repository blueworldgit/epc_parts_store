#!/usr/bin/env python3
"""
Compare serials between Django motorpartsdata models and Oscar catalogue models
Shows which serials exist in Django vs which have been imported to Oscar
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
    
    print('🔍 SERIAL COMPARISON: DJANGO vs OSCAR')
    print('=' * 60)
    
    # Get Django serials
    print('\n📋 DJANGO SERIALS (motorpartsdata_serialnumber)')
    print('-' * 50)
    
    # First check the table structure
    cur.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'motorpartsdata_serialnumber'
        ORDER BY ordinal_position
    """)
    columns = cur.fetchall()
    print(f'Table columns: {[col["column_name"] for col in columns]}')
    
    cur.execute("""
        SELECT serial, vehicle_brand 
        FROM motorpartsdata_serialnumber 
        ORDER BY serial
    """)
    django_serials = cur.fetchall()
    
    print(f'Total Django serials: {len(django_serials)}\n')
    
    django_serial_list = []
    for i, serial in enumerate(django_serials, 1):
        print(f'{i:2d}. {serial["serial"]} - {serial["vehicle_brand"]}')
        django_serial_list.append(serial["serial"])
    
    # Get Oscar serials (look for categories that represent serials)
    print('\n🛒 OSCAR SERIALS (catalogue_category - depth 2)')
    print('-' * 50)
    
    # Serial categories in Oscar are typically at depth 2 (Brand->Serial->Parent->Child)
    cur.execute("""
        SELECT name, slug 
        FROM catalogue_category 
        WHERE depth = 2 
        ORDER BY name
    """)
    oscar_serial_cats = cur.fetchall()
    
    print(f'Total Oscar serial categories: {len(oscar_serial_cats)}\n')
    
    oscar_serial_list = []
    for i, cat in enumerate(oscar_serial_cats, 1):
        cat_name = cat["name"]
        cat_slug = cat["slug"]
        print(f'{i:2d}. {cat_name} (slug: {cat_slug})')
        
        # Try to extract actual serial number from category name
        if 'serial-' in cat_slug:
            # Extract serial from slug like "serial-lsfal11a4pa157987_1234"
            serial_part = cat_slug.split('serial-')[1].split('_')[0].split('-')[0]
            oscar_serial_list.append(serial_part.upper())
    
    # Analysis
    print('\n📊 ANALYSIS')
    print('-' * 20)
    
    django_serials_set = set(django_serial_list)
    oscar_serials_set = set(oscar_serial_list)
    
    print(f'Django serials: {len(django_serials_set)}')
    print(f'Oscar serials: {len(oscar_serials_set)}')
    
    # Serials in Django but not in Oscar
    missing_in_oscar = django_serials_set - oscar_serials_set
    if missing_in_oscar:
        print(f'\n❌ Serials in Django but NOT in Oscar ({len(missing_in_oscar)}):')
        for serial in sorted(missing_in_oscar):
            print(f'   • {serial}')
    else:
        print('\n✅ All Django serials are present in Oscar')
    
    # Serials in Oscar but not in Django (orphaned)
    orphaned_in_oscar = oscar_serials_set - django_serials_set
    if orphaned_in_oscar:
        print(f'\n⚠️  Serials in Oscar but NOT in Django ({len(orphaned_in_oscar)}):')
        for serial in sorted(orphaned_in_oscar):
            print(f'   • {serial}')
    else:
        print('\n✅ No orphaned serials in Oscar')
    
    # Perfect matches
    matching_serials = django_serials_set & oscar_serials_set
    if matching_serials:
        print(f'\n✅ Matching serials ({len(matching_serials)}):')
        for serial in sorted(matching_serials):
            print(f'   • {serial}')
    
    # Close connection
    cur.close()
    conn.close()

if __name__ == '__main__':
    main()
#!/usr/bin/env python3
"""
Quick check if LSH14C4C5NA129710 has Oscar categories yet
"""
import psycopg2
from psycopg2.extras import DictCursor

def main():
    conn = psycopg2.connect(
        host='80.95.207.42',
        database='parts_store', 
        user='postgres',
        password='N0rwich!',
        port=5432
    )
    
    cur = conn.cursor(cursor_factory=DictCursor)
    
    serial_number = 'LSH14C4C5NA129710'
    
    # Check Oscar categories for this serial
    cur.execute("""
        SELECT COUNT(*) as count
        FROM catalogue_category 
        WHERE name ILIKE %s OR slug ILIKE %s
    """, (f'%{serial_number.lower()}%', f'%{serial_number.lower()}%'))
    
    result = cur.fetchone()
    count = result['count']
    
    print(f'🔍 Checking Oscar categories for {serial_number}:')
    print(f'   Found: {count} categories')
    
    if count == 0:
        print('❌ No categories found - need to run fresh import first:')
        print('   1. python scrapeandpush.py ./LSH14C4C5NA129710')  
        print('   2. python manage.py import_to_oscar --serial LSH14C4C5NA129710')
        print('   3. python bulk_attach_images.py')
    else:
        print('✅ Categories exist - bulk_attach_images.py should work')
    
    cur.close()
    conn.close()

if __name__ == '__main__':
    main()
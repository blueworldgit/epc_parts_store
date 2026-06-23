#!/usr/bin/env python3
"""
Check LSH14C4C5NA129710 specific categories and image status
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
    
    print(f'🔍 CHECKING {serial_number} SPECIFIC CATEGORIES:')
    print('=' * 60)
    
    # Get categories for this specific serial
    cur.execute("""
        SELECT name, slug, image, depth
        FROM catalogue_category 
        WHERE name ILIKE %s OR slug ILIKE %s
        ORDER BY depth, name
    """, (f'%{serial_number.lower()}%', f'%{serial_number.lower()}%'))
    
    categories = cur.fetchall()
    
    print(f'Total categories: {len(categories)}')
    
    # Count categories with and without images
    with_images = 0
    without_images = 0
    
    print('\nSample categories (first 10):')
    for i, cat in enumerate(categories[:10], 1):
        has_image = bool(cat['image'] and cat['image'].strip())
        if has_image:
            with_images += 1
            status = '🖼️  HAS IMAGE'
        else:
            without_images += 1  
            status = '❌ NO IMAGE'
            
        print(f'{i:2d}. {status} - {cat["name"][:60]}...')
        print(f'    Depth: {cat["depth"]}, Slug: {cat["slug"][:40]}...')
    
    # Count all categories with/without images
    for cat in categories[10:]:
        has_image = bool(cat['image'] and cat['image'].strip())
        if has_image:
            with_images += 1
        else:
            without_images += 1
    
    print(f'\n📊 IMAGE STATUS SUMMARY:')
    print(f'   Categories WITH images: {with_images}')
    print(f'   Categories WITHOUT images: {without_images}')
    print(f'   Coverage: {(with_images/len(categories)*100):.1f}%')
    
    if without_images > with_images:
        print('\n💡 SOLUTION: Run bulk_attach_images.py again with:')
        print('   - Check that image names in Rentals folder match category names')
        print('   - Or lower similarity threshold (currently 60%)')
        print('   - Or add more specific images to Rentals folder')
    
    cur.close()
    conn.close()

if __name__ == '__main__':
    main()
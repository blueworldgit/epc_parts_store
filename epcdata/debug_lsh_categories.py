#!/usr/bin/env python3
"""
Compare LSH14C4C5NA129710 category names vs other serials to see why images aren't matching
"""
import psycopg2
from psycopg2.extras import DictCursor

def clean_category_name(name):
    """Clean category name same way as bulk_attach_images.py"""
    if name and " - " in name:
        return name.split(" - ", 1)[1].strip()
    return name.strip() if name else ""

def main():
    conn = psycopg2.connect(
        host='80.95.207.42',
        database='parts_store', 
        user='postgres',
        password='N0rwich!',
        port=5432
    )
    
    cur = conn.cursor(cursor_factory=DictCursor)
    
    print('🔍 COMPARING LSH14C4C5NA129710 CATEGORIES VS OTHER SERIALS')
    print('=' * 70)
    
    # Get sample categories from LSH14C4C5NA129710 without images
    cur.execute("""
        SELECT name, slug, image, depth
        FROM catalogue_category 
        WHERE (name ILIKE %s OR slug ILIKE %s)
        AND (image IS NULL OR image = '')
        AND depth >= 3
        ORDER BY name
        LIMIT 10
    """, ('%lsh14c4c5na129710%', '%lsh14c4c5na129710%'))
    
    lsh_categories = cur.fetchall()
    
    print(f'📋 LSH14C4C5NA129710 categories WITHOUT images (first 10):')
    for i, cat in enumerate(lsh_categories, 1):
        cleaned_name = clean_category_name(cat['name'])
        print(f'{i:2d}. {cat["name"]}')
        print(f'    Cleaned: "{cleaned_name}"')
        print(f'    Slug: {cat["slug"]}')
        
        # Check if other serials have this same cleaned name WITH images
        cur.execute("""
            SELECT name, slug, image
            FROM catalogue_category 
            WHERE name != %s 
            AND (image IS NOT NULL AND image != '')
            ORDER BY name
            LIMIT 3
        """, (cat['name'],))
        
        similar_with_images = cur.fetchall()
        
        # Filter by cleaned name similarity
        matching_others = []
        for other_cat in similar_with_images:
            other_cleaned = clean_category_name(other_cat['name'])
            if other_cleaned.lower() == cleaned_name.lower():
                matching_others.append(other_cat)
        
        if matching_others:
            print(f'    🖼️  OTHER serials with SAME cleaned name that HAVE images:')
            for other in matching_others[:2]:
                print(f'       • {other["name"]} ✅')
        else:
            print(f'    ❌ No other categories found with cleaned name: "{cleaned_name}"')
        print()
    
    # Check available images in Rentals
    print('\n📷 AVAILABLE IMAGES IN RENTALS:')
    available_images = [
        'Accessory Switches', 'Antenna', 'Baffle Plate-Ware', 'Battery Harnesses',
        'Accessory & Accessory Drive', 'Air Filter', 'Airbag', 'Air Intake System', 
        'Battery & Electrical Energy Storage', 'Accelerator Pedal', 'Air Bag Control Unit',
        'Arrangement for VAN Vehicle (UK_HK)'
    ]
    
    for img in available_images:
        print(f'   • {img}.png')
    
    print('\n💡 RECOMMENDATION:')
    print('The issue is likely that LSH14C4C5NA129710 categories have different part number prefixes')
    print('or slightly different category names that are not being matched by the similarity algorithm.')
    print('\nNext step: Check if we can modify bulk_attach_images.py to be more permissive')
    print('or manually map specific LSH14C4C5NA129710 category names.')
    
    cur.close()
    conn.close()

if __name__ == '__main__':
    main()
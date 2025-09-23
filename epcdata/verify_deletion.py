#!/usr/bin/env python
"""
Verify Serial Data Removal

Check if all data for LSFAL11A4PA157987 has been removed from production.
"""

import psycopg2

def verify_deletion():
    print("✅ VERIFYING SERIAL DATA REMOVAL")
    print("="*50)
    
    conn = psycopg2.connect(
        host='80.95.207.42',
        database='parts_store',
        user='postgres',
        password='N0rwich!',
        port=5432
    )
    
    cursor = conn.cursor()
    serial = 'LSFAL11A4PA157987'
    
    print(f"🔍 Checking for remaining data for serial: {serial}")
    print()
    
    # Check categories
    cursor.execute("""
        SELECT COUNT(*) FROM catalogue_category 
        WHERE slug LIKE %s
    """, (f'%{serial}%',))
    
    category_count = cursor.fetchone()[0]
    print(f"📁 Categories remaining: {category_count}")
    
    if category_count > 0:
        # Show what categories remain
        cursor.execute("""
            SELECT name, slug FROM catalogue_category 
            WHERE slug LIKE %s
            ORDER BY slug
        """, (f'%{serial}%',))
        
        remaining_cats = cursor.fetchall()
        print("   Remaining categories:")
        for cat in remaining_cats:
            print(f"     • {cat[0]} ({cat[1]})")
    
    # Check products
    cursor.execute("""
        SELECT COUNT(DISTINCT p.id)
        FROM catalogue_product p
        JOIN catalogue_productcategory pc ON p.id = pc.product_id
        JOIN catalogue_category c ON pc.category_id = c.id
        WHERE c.slug LIKE %s
    """, (f'%{serial}%',))
    
    product_count = cursor.fetchone()[0]
    print(f"📦 Products remaining: {product_count}")
    
    # Check for orphaned products (products that might exist but not be linked)
    cursor.execute("""
        SELECT COUNT(*) FROM catalogue_product p
        WHERE p.title LIKE %s OR p.slug LIKE %s
    """, (f'%{serial}%', f'%{serial}%'))
    
    orphan_products = cursor.fetchone()[0]
    print(f"👻 Orphaned products: {orphan_products}")
    
    # Check product-category relationships
    cursor.execute("""
        SELECT COUNT(*) FROM catalogue_productcategory pc
        JOIN catalogue_category c ON pc.category_id = c.id
        WHERE c.slug LIKE %s
    """, (f'%{serial}%',))
    
    relationship_count = cursor.fetchone()[0]
    print(f"🔗 Product-category relationships: {relationship_count}")
    
    # Check stock records
    cursor.execute("""
        SELECT COUNT(*) FROM partner_stockrecord sr
        JOIN catalogue_product p ON sr.product_id = p.id
        JOIN catalogue_productcategory pc ON p.id = pc.product_id
        JOIN catalogue_category c ON pc.category_id = c.id
        WHERE c.slug LIKE %s
    """, (f'%{serial}%',))
    
    stock_count = cursor.fetchone()[0]
    print(f"📊 Stock records: {stock_count}")
    
    # Check for the brand record itself
    cursor.execute("""
        SELECT name, slug FROM catalogue_category 
        WHERE slug = %s
    """, (f'serial-{serial}',))
    
    brand_record = cursor.fetchone()
    if brand_record:
        print(f"\\n🏷️  BRAND RECORD FOUND:")
        print(f"   Name: {brand_record[0]}")
        print(f"   Slug: {brand_record[1]}")
        print("   ✅ Ready for fresh import!")
    else:
        print(f"\\n❌ Brand record missing: serial-{serial}")
        print("   ⚠️  You may need to recreate the brand record")
    
    # Summary
    print(f"\\n📊 DELETION VERIFICATION SUMMARY:")
    print("="*40)
    
    total_remaining = category_count + product_count + relationship_count + stock_count
    
    if total_remaining == 0:
        print("✅ COMPLETE DELETION CONFIRMED!")
        print("   🎉 All product data successfully removed")
        print("   🚀 Ready for fresh import")
    else:
        print("⚠️  PARTIAL DELETION DETECTED")
        print(f"   📊 Total remaining items: {total_remaining}")
        print("   🔧 May need manual cleanup")
    
    if brand_record:
        print(f"✅ Brand preserved: {brand_record[0]}")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    verify_deletion()
#!/usr/bin/env python3
"""
Diagnose Oscar category structure and product relationships for LSFAL11A4PA157987
"""
import psycopg2
from psycopg2.extras import RealDictCursor

def main():
    print('🔍 OSCAR CATEGORY RELATIONSHIP DIAGNOSIS')
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
        
        # First, find all categories for this serial
        print('\n📁 OSCAR CATEGORY STRUCTURE')
        print('=' * 30)
        
        cur.execute("""
            SELECT id, name, slug, path, depth, numchild 
            FROM catalogue_category 
            WHERE name ILIKE '%lsfal11a4pa157987%' 
            ORDER BY depth, name
        """)
        all_categories = cur.fetchall()
        
        print(f"Found {len(all_categories)} categories:")
        for cat in all_categories:
            indent = "  " * cat['depth']
            print(f"{indent}• {cat['name']} (ID: {cat['id']}, depth: {cat['depth']}, children: {cat['numchild']})")
            print(f"{indent}  slug: {cat['slug']}")
            print(f"{indent}  path: {cat['path']}")
        
        # Check product-category relationships
        print('\n📦 PRODUCT-CATEGORY RELATIONSHIPS')
        print('=' * 35)
        
        if all_categories:
            category_ids = [cat['id'] for cat in all_categories]
            placeholders = ','.join(['%s'] * len(category_ids))
            
            cur.execute(f"""
                SELECT c.name as category_name, c.depth, COUNT(pc.product_id) as product_count
                FROM catalogue_category c
                LEFT JOIN catalogue_productcategory pc ON c.id = pc.category_id
                WHERE c.id IN ({placeholders})
                GROUP BY c.id, c.name, c.depth
                ORDER BY c.depth, c.name
            """, category_ids)
            
            cat_products = cur.fetchall()
            
            total_products = 0
            for cat in cat_products:
                total_products += cat['product_count']
                indent = "  " * cat['depth']
                print(f"{indent}• {cat['category_name']}: {cat['product_count']} products")
            
            print(f"\n📊 Total products across all categories: {total_products}")
        
        # Check if products exist but are assigned to wrong categories
        print('\n🔍 PRODUCT INVESTIGATION')
        print('=' * 25)
        
        cur.execute("SELECT COUNT(*) as count FROM catalogue_product WHERE title ILIKE '%LSFAL11A4PA157987%'")
        lsfal_products = cur.fetchone()['count']
        print(f"📦 Products with LSFAL in title: {lsfal_products}")
        
        if lsfal_products > 0:
            # Sample LSFAL products and their categories
            cur.execute("""
                SELECT p.id, p.title, p.slug 
                FROM catalogue_product p 
                WHERE p.title ILIKE '%LSFAL11A4PA157987%' 
                LIMIT 5
            """)
            sample_products = cur.fetchall()
            
            print("Sample LSFAL products:")
            for product in sample_products:
                print(f"   • {product['title']} (ID: {product['id']})")
                
                # Check this product's categories
                cur.execute("""
                    SELECT c.name, c.depth, c.slug 
                    FROM catalogue_category c
                    JOIN catalogue_productcategory pc ON c.id = pc.category_id
                    WHERE pc.product_id = %s
                    ORDER BY c.depth
                """, (product['id'],))
                product_cats = cur.fetchall()
                
                if product_cats:
                    print("     Categories:")
                    for cat in product_cats:
                        indent = "       " + ("  " * cat['depth'])
                        print(f"{indent}└─ {cat['name']} (depth: {cat['depth']})")
                else:
                    print("     ❌ NO CATEGORIES ASSIGNED!")
        
        # Check the specific URL that's failing
        print('\n🎯 SPECIFIC URL ANALYSIS')
        print('=' * 25)
        
        # The failing URL suggests we need: Parent-12 -> Child-1_40
        failing_slug = "serial-lsfal11a4pa157987-parent-12-child-1_40"
        
        cur.execute("SELECT * FROM catalogue_category WHERE slug = %s", (failing_slug,))
        failing_category = cur.fetchone()
        
        if failing_category:
            print(f"✅ Found category: {failing_category['name']}")
            
            # Check products in this specific category
            cur.execute("""
                SELECT COUNT(*) as count FROM catalogue_productcategory 
                WHERE category_id = %s
            """, (failing_category['id'],))
            product_count = cur.fetchone()['count']
            print(f"📦 Products in this category: {product_count}")
            
            if product_count == 0:
                print("❌ This explains why the URL shows no products!")
                
                # Check if parent category has products
                parent_slug = "serial-lsfal11a4pa157987-parent-12"
                cur.execute("SELECT * FROM catalogue_category WHERE slug = %s", (parent_slug,))
                parent_cat = cur.fetchone()
                if parent_cat:
                    cur.execute("""
                        SELECT COUNT(*) as count FROM catalogue_productcategory 
                        WHERE category_id = %s
                    """, (parent_cat['id'],))
                    parent_products = cur.fetchone()['count']
                    print(f"📁 Parent category products: {parent_products}")
        else:
            print(f"❌ Category not found: {failing_slug}")
            
            # Look for similar categories
            cur.execute("""
                SELECT name, slug FROM catalogue_category 
                WHERE name ILIKE '%parent-12%' AND name ILIKE '%lsfal11a4pa157987%'
            """)
            similar_cats = cur.fetchall()
            
            if similar_cats:
                print("🔍 Similar categories found:")
                for cat in similar_cats:
                    print(f"   • {cat['name']} (slug: {cat['slug']})")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Database error: {e}")

if __name__ == '__main__':
    main()
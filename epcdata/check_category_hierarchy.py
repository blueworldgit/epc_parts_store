#!/usr/bin/env python3
"""
Check the complete Oscar category hierarchy for LSFAL11A4PA157987
"""
import psycopg2
from psycopg2.extras import RealDictCursor

def main():
    print('🔍 COMPLETE OSCAR CATEGORY HIERARCHY')
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
        
        # Find the root serial category
        cur.execute("SELECT * FROM catalogue_category WHERE name = 'Serial LSFAL11A4PA157987'")
        root_cat = cur.fetchone()
        
        if root_cat:
            print(f"\n🎯 ROOT CATEGORY: {root_cat['name']}")
            print(f"   ID: {root_cat['id']}, Slug: {root_cat['slug']}")
            print(f"   Path: {root_cat['path']}, Depth: {root_cat['depth']}")
            print(f"   Children: {root_cat['numchild']}")
            
            # Get the complete hierarchy under this root
            cur.execute("""
                SELECT name, slug, path, depth, numchild, id,
                       (SELECT COUNT(*) FROM catalogue_productcategory WHERE category_id = catalogue_category.id) as product_count
                FROM catalogue_category 
                WHERE path LIKE %s 
                ORDER BY path, name
            """, (root_cat['path'] + '%',))
            
            hierarchy = cur.fetchall()
            print(f"\n📁 COMPLETE HIERARCHY ({len(hierarchy)} categories):")
            print("=" * 50)
            
            # Group by depth for better visualization
            by_depth = {}
            for cat in hierarchy:
                depth = cat['depth']
                if depth not in by_depth:
                    by_depth[depth] = []
                by_depth[depth].append(cat)
            
            for depth in sorted(by_depth.keys()):
                categories = by_depth[depth]
                level_name = ['Brand', 'Serial', 'Parent', 'Child'][depth] if depth < 4 else f'Level-{depth}'
                print(f"\n{level_name} Level (Depth {depth}): {len(categories)} categories")
                
                for cat in categories[:10]:  # Show first 10 of each level
                    indent = "  " * (depth - 2)  # Start indent from serial level
                    products_info = f" ({cat['product_count']} products)" if cat['product_count'] > 0 else ""
                    print(f"{indent}• {cat['name']}{products_info}")
                    print(f"{indent}  slug: {cat['slug']}")
                    
                if len(categories) > 10:
                    print(f"{indent}... and {len(categories) - 10} more")
            
            # Now let's specifically look for Parent-12 and its children
            print(f"\n🎯 SEARCHING FOR PARENT-12 STRUCTURE")
            print("=" * 35)
            
            cur.execute("""
                SELECT * FROM catalogue_category 
                WHERE path LIKE %s AND name ILIKE '%parent%' 
                ORDER BY name
            """, (root_cat['path'] + '%',))
            
            parent_cats = cur.fetchall()
            parent_12 = None
            
            for parent in parent_cats:
                if 'parent' in parent['name'].lower():
                    print(f"• {parent['name']} (slug: {parent['slug']})")
                    if '12' in parent['name']:
                        parent_12 = parent
                        print(f"  ⭐ This might be Parent-12!")
            
            if parent_12:
                print(f"\n🔍 CHILDREN OF POTENTIAL PARENT-12:")
                print("=" * 35)
                
                # Get children of this parent
                cur.execute("""
                    SELECT * FROM catalogue_category 
                    WHERE path LIKE %s AND depth = %s
                    ORDER BY name
                """, (parent_12['path'] + '%', parent_12['depth'] + 1))
                
                children = cur.fetchall()
                for child in children:
                    product_count_query = """
                        SELECT COUNT(*) as count FROM catalogue_productcategory 
                        WHERE category_id = %s
                    """
                    cur.execute(product_count_query, (child['id'],))
                    child_products = cur.fetchone()['count']
                    
                    print(f"   • {child['name']} ({child_products} products)")
                    print(f"     slug: {child['slug']}")
                    
                    # Check if this could be "Child-1_40"
                    if '1' in child['name'] and ('40' in child['name'] or 'child' in child['name'].lower()):
                        print(f"     ⭐ This might be Child-1_40!")
            
        else:
            print("❌ Root serial category not found")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Database error: {e}")

if __name__ == '__main__':
    main()
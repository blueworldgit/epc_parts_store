#!/usr/bin/env python
"""
Simple Production Database Analyzer

Direct connection to analyze the production database issue.
"""

import psycopg2
import json


def analyze_production_database():
    """Connect to production and analyze the issue"""
    print("🌐 PRODUCTION DATABASE ANALYSIS")
    print("="*60)
    
    # Database connection
    conn = psycopg2.connect(
        host='80.95.207.42',
        database='parts_store',
        user='postgres',
        password='N0rwich!',
        port=5432
    )
    
    cursor = conn.cursor()
    
    try:
        print("✅ Connected to production database")
        
        # 1. Check categories for the problematic serial
        serial = 'LSFAL11A4PA157987'
        print(f"\\n🔍 ANALYZING CATEGORIES FOR {serial}")
        print("-"*40)
        
        cursor.execute("""
            SELECT id, name, slug
            FROM catalogue_category 
            WHERE slug LIKE %s AND slug LIKE '%parent-12%'
            ORDER BY slug;
        """, (f'%{serial}%',))
        
        parent12_categories = cursor.fetchall()
        print(f"Found {len(parent12_categories)} Parent-12 categories:")
        
        for row in parent12_categories:
            cat_id, name, slug = row
            # Check products in this category
            cursor.execute("""
                SELECT COUNT(*)
                FROM catalogue_productcategory 
                WHERE category_id = %s;
            """, (cat_id,))
            
            count_result = cursor.fetchone()
            product_count = count_result[0] if count_result else 0
            print(f"  📁 {name}")
            print(f"     Slug: {slug}")
            print(f"     Products: {product_count}")
            
            if product_count == 0:
                print("     ❌ EMPTY CATEGORY - THIS IS THE PROBLEM!")
            
        # 2. Find ALL energy storage products for this serial
        print(f"\\n⚡ FINDING ALL ENERGY STORAGE PRODUCTS FOR {serial}")
        print("-"*40)
        
        cursor.execute("""
            SELECT 
                p.title,
                c.name as category_name,
                c.slug as category_slug
            FROM catalogue_product p
            JOIN catalogue_productcategory pc ON p.id = pc.product_id
            JOIN catalogue_category c ON pc.category_id = c.id
            WHERE c.slug LIKE %s
            AND (
                UPPER(p.title) LIKE '%BATTERY%' OR
                UPPER(p.title) LIKE '%ENERGY%' OR
                UPPER(p.title) LIKE '%POWER%' OR
                UPPER(p.title) LIKE '%ELECTRICAL%' OR
                UPPER(p.title) LIKE '%TRAY%' OR
                UPPER(p.title) LIKE '%INTELLIGENT%'
            )
            ORDER BY c.slug;
        """, (f'%{serial}%',))
        
        products = cursor.fetchall()
        print(f"Found {len(products)} energy storage products:")
        
        # Group by parent
        by_parent = {}
        
        for row in products:
            title, cat_name, cat_slug = row
            print(f"\\n  ⚡ {title}")
            print(f"     Category: {cat_name}")
            print(f"     Slug: {cat_slug}")
            
            # Extract parent number
            parts = cat_slug.split('-')
            parent_num = 'unknown'
            for i, part in enumerate(parts):
                if part == 'parent' and i + 1 < len(parts):
                    parent_num = parts[i + 1]
                    break
            
            print(f"     Parent: {parent_num}")
            
            if parent_num not in by_parent:
                by_parent[parent_num] = []
            by_parent[parent_num].append(title)
        
        # 3. Summary
        print(f"\\n📊 SUMMARY:")
        print("-"*40)
        for parent, prods in sorted(by_parent.items()):
            print(f"  Parent-{parent}: {len(prods)} energy storage products")
        
        # 4. Check what's in parent-2 (where energy storage should be)
        print(f"\\n🎯 CHECKING PARENT-2 CATEGORIES FOR {serial}")
        print("-"*40)
        
        cursor.execute("""
            SELECT c.id, c.name, c.slug, COUNT(pc.product_id) as product_count
            FROM catalogue_category c
            LEFT JOIN catalogue_productcategory pc ON c.id = pc.category_id
            WHERE c.slug LIKE %s AND c.slug LIKE '%parent-2%'
            GROUP BY c.id, c.name, c.slug
            ORDER BY c.slug;
        """, (f'%{serial}%',))
        
        parent2_categories = cursor.fetchall()
        print(f"Found {len(parent2_categories)} Parent-2 categories:")
        
        for row in parent2_categories:
            cat_id, name, slug, product_count = row
            print(f"  📁 {name}")
            print(f"     Slug: {slug}")
            print(f"     Products: {product_count}")
            
            if product_count > 0:
                # Show what products are in here
                cursor.execute("""
                    SELECT p.title
                    FROM catalogue_product p
                    JOIN catalogue_productcategory pc ON p.id = pc.product_id
                    WHERE pc.category_id = %s
                    LIMIT 5;
                """, (cat_id,))
                
                sample_products = cursor.fetchall()
                print("     Sample products:")
                for row in sample_products:
                    title = row[0]
                    print(f"       • {title}")
        
        print("\\n✅ Analysis complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    analyze_production_database()
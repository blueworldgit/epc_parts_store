#!/usr/bin/env python
"""
Direct PostgreSQL Connection to Production Server

This script connects directly to your production PostgreSQL database
without Django interference.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime


class DirectProductionAnalyzer:
    def __init__(self):
        # Your production database credentials
        self.db_config = {
            'host': '80.95.207.42',
            'database': 'parts_store',
            'user': 'postgres',
            'password': 'N0rwich!',
            'port': 5432
        }
        self.connection = None
        
    def connect(self):
        """Connect directly to production PostgreSQL"""
        print("🔌 CONNECTING TO PRODUCTION DATABASE...")
        print("="*60)
        print(f"🎯 Host: {self.db_config['host']}")
        print(f"🗄️ Database: {self.db_config['database']}")
        
        try:
            self.connection = psycopg2.connect(**self.db_config)
            print("✅ Connected successfully!")
            
            # Test the connection
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT version();")
                version = cursor.fetchone()[0]
                print(f"✅ PostgreSQL Version: {version}")
                
                cursor.execute("SELECT current_database();")
                db_name = cursor.fetchone()[0]
                print(f"✅ Current Database: {db_name}")
                
            return True
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def check_database_tables(self):
        """Check what tables exist in the database"""
        print("\\n🔍 CHECKING DATABASE STRUCTURE...")
        print("="*60)
        
        try:
            with self.connection.cursor() as cursor:
                # Check for Oscar tables
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name LIKE '%catalogue%'
                    ORDER BY table_name;
                """)
                
                tables = cursor.fetchall()
                print(f"Found {len(tables)} catalogue-related tables:")
                
                for table in tables:
                    table_name = table[0]
                    print(f"  📋 {table_name}")
                    
                    # Count records in each table
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                    count = cursor.fetchone()[0]
                    print(f"     Records: {count}")
                
                return [table[0] for table in tables]
                
        except Exception as e:
            print(f"❌ Error checking tables: {e}")
            return []
    
    def analyze_categories_for_serial(self, serial='LSFAL11A4PA157987'):
        """Analyze categories for the specific serial"""
        print(f"\\n🎯 ANALYZING CATEGORIES FOR SERIAL: {serial}")
        print("="*60)
        
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                # Find categories that match this serial
                cursor.execute("""
                    SELECT id, name, slug, path, depth
                    FROM catalogue_category 
                    WHERE slug LIKE %s
                    ORDER BY slug;
                """, (f'%{serial}%',))
                
                categories = cursor.fetchall()
                print(f"Found {len(categories)} categories for {serial}:")
                
                parent_12_categories = []
                parent_2_categories = []
                all_categories = []
                
                for cat in categories:
                    print(f"\\n📁 {cat['name']}")
                    print(f"   ID: {cat['id']}")
                    print(f"   Slug: {cat['slug']}")
                    print(f"   Depth: {cat['depth']}")
                    
                    # Check for products in this category
                    cursor.execute("""
                        SELECT COUNT(*)
                        FROM catalogue_productcategory pc
                        WHERE pc.category_id = %s;
                    """, (cat['id'],))
                    
                    product_count = cursor.fetchone()
                    if product_count:
                        product_count = product_count[0]
                    else:
                        product_count = 0
                    print(f"   Products: {product_count}")
                    
                    # Categorize by parent
                    if 'parent-12' in cat['slug']:
                        parent_12_categories.append({**cat, 'product_count': product_count})
                    elif 'parent-2' in cat['slug']:
                        parent_2_categories.append({**cat, 'product_count': product_count})
                    
                    all_categories.append({**cat, 'product_count': product_count})
                
                print(f"\\n📊 SUMMARY:")
                print(f"   Parent-12 categories: {len(parent_12_categories)}")
                print(f"   Parent-2 categories: {len(parent_2_categories)}")
                print(f"   Total categories: {len(all_categories)}")
                
                return {
                    'parent_12': parent_12_categories,
                    'parent_2': parent_2_categories,
                    'all': all_categories
                }
                
        except Exception as e:
            print(f"❌ Error analyzing categories: {e}")
            return None
    
    def find_energy_storage_products(self, serial='LSFAL11A4PA157987'):
        """Find all energy storage products for this serial"""
        print(f"\\n⚡ FINDING ENERGY STORAGE PRODUCTS FOR {serial}")
        print("="*60)
        
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                # Find products with energy-related titles in categories for this serial
                cursor.execute("""
                    SELECT 
                        p.id as product_id,
                        p.title,
                        c.id as category_id,
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
                        UPPER(p.title) LIKE '%TRAY ASSEMBLY%' OR
                        UPPER(p.title) LIKE '%INTELLIGENT%' OR
                        UPPER(p.title) LIKE '%BOARD%'
                    )
                    ORDER BY c.slug, p.title;
                """, (f'%{serial}%',))
                
                products = cursor.fetchall()
                print(f"Found {len(products)} energy storage products:")
                
                # Group by parent number
                by_parent = {}
                
                for product in products:
                    print(f"\\n⚡ {product['title']}")
                    print(f"   Category: {product['category_name']}")
                    print(f"   Slug: {product['category_slug']}")
                    
                    # Extract parent number
                    slug_parts = product['category_slug'].split('-')
                    parent_num = 'unknown'
                    for i, part in enumerate(slug_parts):
                        if part == 'parent' and i + 1 < len(slug_parts):
                            parent_num = slug_parts[i + 1]
                            break
                    
                    print(f"   Parent: {parent_num}")
                    
                    if parent_num not in by_parent:
                        by_parent[parent_num] = []
                    by_parent[parent_num].append(product)
                
                print(f"\\n📊 DISTRIBUTION BY PARENT:")
                for parent, prods in sorted(by_parent.items()):
                    print(f"   Parent-{parent}: {len(prods)} products")
                
                return products, by_parent
                
        except Exception as e:
            print(f"❌ Error finding products: {e}")
            return [], {}
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            print("\\n🔌 Database connection closed.")
    
    def run(self):
        """Main execution method"""
        print("🌐 DIRECT PRODUCTION DATABASE ANALYZER")
        print("="*60)
        
        # Step 1: Connect
        if not self.connect():
            return False
        
        try:
            # Step 2: Check database structure
            tables = self.check_database_tables()
            
            if not tables:
                print("❌ No catalogue tables found!")
                return False
            
            # Step 3: Analyze categories for the problematic serial
            categories = self.analyze_categories_for_serial()
            
            # Step 4: Find energy storage products
            products, by_parent = self.find_energy_storage_products()
            
            # Step 5: Focus on the URL issue
            if categories and 'parent_12' in categories:
                print(f"\\n🎯 FOCUSING ON PARENT-12 CATEGORIES (URL TARGET):")
                for cat in categories['parent_12']:
                    if cat['product_count'] == 0:
                        print(f"   ❌ EMPTY: {cat['name']} ({cat['slug']})")
                    else:
                        print(f"   ✅ HAS PRODUCTS: {cat['name']} - {cat['product_count']} products")
            
            return True
            
        finally:
            self.close()


if __name__ == "__main__":
    analyzer = DirectProductionAnalyzer()
    analyzer.run()
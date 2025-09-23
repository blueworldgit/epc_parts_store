#!/usr/bin/env python3
"""
Check production database table structure and data
"""
import psycopg2
from psycopg2.extras import RealDictCursor

def main():
    print('🔍 PRODUCTION DATABASE STRUCTURE CHECK')
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
        
        # Check table structures first
        print('\n📋 TABLE STRUCTURES')
        print('=' * 30)
        
        # Check SerialNumber table structure
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'motorpartsdata_serialnumber'
            ORDER BY ordinal_position
        """)
        serial_cols = cur.fetchall()
        if serial_cols:
            print("SerialNumber table columns:")
            for col in serial_cols:
                print(f"   • {col['column_name']} ({col['data_type']})")
        else:
            print("❌ SerialNumber table not found")
        
        # Check if any tables exist with LSFAL data
        print('\n🔍 SEARCHING FOR LSFAL DATA')
        print('=' * 30)
        
        # Check all tables for LSFAL references
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND (table_name LIKE '%serial%' OR table_name LIKE '%motorparts%' OR table_name LIKE '%catalogue%')
            ORDER BY table_name
        """)
        tables = cur.fetchall()
        
        print(f"Found {len(tables)} relevant tables:")
        for table in tables:
            table_name = table['table_name']
            print(f"   • {table_name}")
            
            # Try to find LSFAL data in each table
            try:
                # First check if table has any LSFAL-related columns or data
                cur.execute(f"SELECT * FROM {table_name} LIMIT 1")
                sample = cur.fetchone()
                if sample:
                    # Check if any values contain LSFAL
                    has_lsfal = any('LSFAL11A4PA157987' in str(value).upper() for value in sample.values() if value)
                    if has_lsfal:
                        cur.execute(f"SELECT COUNT(*) as count FROM {table_name}")
                        count = cur.fetchone()['count']
                        print(f"     └─ Contains LSFAL data! Total rows: {count}")
            except Exception as e:
                print(f"     └─ Error checking table: {e}")
        
        # Check Oscar catalogue specifically
        print('\n🛒 OSCAR CATALOGUE CHECK')
        print('=' * 30)
        
        # Look for categories with LSFAL
        cur.execute("SELECT COUNT(*) as count FROM catalogue_category WHERE name ILIKE '%lsfal11a4pa157987%'")
        cat_count = cur.fetchone()['count']
        print(f"📁 Categories with LSFAL: {cat_count}")
        
        if cat_count > 0:
            cur.execute("SELECT id, name, slug FROM catalogue_category WHERE name ILIKE '%lsfal11a4pa157987%' LIMIT 5")
            categories = cur.fetchall()
            for cat in categories:
                print(f"   • {cat['name']} (ID: {cat['id']}, slug: {cat['slug']})")
        
        # Look for products with LSFAL
        cur.execute("SELECT COUNT(*) as count FROM catalogue_product WHERE title ILIKE '%lsfal11a4pa157987%'")
        prod_count = cur.fetchone()['count']
        print(f"📦 Products with LSFAL: {prod_count}")
        
        # Check product-category relationships
        cur.execute("""
            SELECT COUNT(*) as count FROM catalogue_productcategory pc 
            JOIN catalogue_category c ON pc.category_id = c.id 
            WHERE c.name ILIKE '%lsfal11a4pa157987%'
        """)
        rel_count = cur.fetchone()['count']
        print(f"🔗 Product-category relationships: {rel_count}")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Database error: {e}")

if __name__ == '__main__':
    main()
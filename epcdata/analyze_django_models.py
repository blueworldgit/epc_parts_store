#!/usr/bin/env python3
"""
Check Django model data for LSFAL11A4PA157987 to see why products didn't import
"""
import psycopg2
from psycopg2.extras import RealDictCursor

def main():
    print('🔍 DJANGO MODEL DATA ANALYSIS')
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
        
        # Check SerialNumber data (note: column is 'serial', not 'serial_number')
        print('\n📋 DJANGO SERIALNUMBER DATA')
        print('=' * 30)
        
        cur.execute("SELECT * FROM motorpartsdata_serialnumber WHERE serial = 'LSFAL11A4PA157987'")
        serial = cur.fetchone()
        if serial:
            print(f"📋 Django Serial: {serial['serial']} - {serial['vehicle_brand']} (ID: {serial['id']})")
            
            # Check ParentTitles
            cur.execute("SELECT COUNT(*) as count FROM motorpartsdata_parenttitle WHERE serial_number_id = %s", (serial['id'],))
            parent_count = cur.fetchone()['count']
            print(f"📁 Django Parents: {parent_count}")
            
            if parent_count > 0:
                # Sample parent titles
                cur.execute("SELECT * FROM motorpartsdata_parenttitle WHERE serial_number_id = %s LIMIT 3", (serial['id'],))
                sample_parents = cur.fetchall()
                print("   Sample parents:")
                for parent in sample_parents:
                    print(f"     • {parent['title']} (ID: {parent['id']})")
            
            # Check ChildTitles
            cur.execute("""
                SELECT COUNT(*) as count FROM motorpartsdata_childtitle ct 
                JOIN motorpartsdata_parenttitle pt ON ct.parent_title_id = pt.id 
                WHERE pt.serial_number_id = %s
            """, (serial['id'],))
            child_count = cur.fetchone()['count']
            print(f"📂 Django Children: {child_count}")
            
            if child_count > 0:
                # Sample child titles
                cur.execute("""
                    SELECT ct.*, pt.title as parent_title FROM motorpartsdata_childtitle ct 
                    JOIN motorpartsdata_parenttitle pt ON ct.parent_title_id = pt.id 
                    WHERE pt.serial_number_id = %s LIMIT 3
                """, (serial['id'],))
                sample_children = cur.fetchall()
                print("   Sample children:")
                for child in sample_children:
                    print(f"     • {child['title']} under {child['parent_title']} (ID: {child['id']})")
            
            # Check Parts
            cur.execute("SELECT COUNT(*) as count FROM motorpartsdata_part WHERE serial_number_id = %s", (serial['id'],))
            part_count = cur.fetchone()['count']
            print(f"🔧 Django Parts: {part_count}")
            
            if part_count > 0:
                # Sample parts with full details
                cur.execute("""
                    SELECT p.*, ct.title as child_title, pt.title as parent_title 
                    FROM motorpartsdata_part p 
                    JOIN motorpartsdata_childtitle ct ON p.child_title_id = ct.id
                    JOIN motorpartsdata_parenttitle pt ON ct.parent_title_id = pt.id
                    WHERE p.serial_number_id = %s 
                    LIMIT 5
                """, (serial['id'],))
                sample_parts = cur.fetchall()
                print("   Sample parts:")
                for part in sample_parts:
                    print(f"     • {part['part_number']} -> {part['child_title']} (Parent: {part['parent_title']})")
                    print(f"       Description: {part.get('description', 'N/A')}")
                    print(f"       Price: £{part.get('price', 'N/A')}")
            
            # Summary for import process
            print(f"\n🔍 IMPORT READINESS CHECK")
            print("=" * 30)
            print(f"✅ Serial exists: {serial['serial']}")
            print(f"✅ Parent categories: {parent_count}")
            print(f"✅ Child categories: {child_count}")
            print(f"✅ Products to import: {part_count}")
            
            if part_count == 0:
                print("❌ NO PARTS TO IMPORT! This explains why no products appeared.")
            elif parent_count == 0:
                print("❌ NO PARENT CATEGORIES! Import would fail.")
            elif child_count == 0:
                print("❌ NO CHILD CATEGORIES! Import would fail.")
            else:
                print("✅ All data present - import should work")
        else:
            print('❌ No Django serial found in production')
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Database error: {e}")

if __name__ == '__main__':
    main()
#!/usr/bin/env python3
"""
Check exact table structures for Django models
"""
import psycopg2
from psycopg2.extras import RealDictCursor

def main():
    print('🔍 DJANGO MODEL TABLE STRUCTURES')
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
        
        # Check all Django model table structures
        tables = ['motorpartsdata_serialnumber', 'motorpartsdata_parenttitle', 'motorpartsdata_childtitle', 'motorpartsdata_part']
        
        for table in tables:
            print(f'\n📋 {table.upper()}')
            print('=' * (len(table) + 4))
            
            cur.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = %s
                ORDER BY ordinal_position
            """, (table,))
            columns = cur.fetchall()
            
            for col in columns:
                nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
                print(f"   • {col['column_name']} ({col['data_type']}) {nullable}")
        
        # Now get actual data counts
        print(f'\n🔢 DATA COUNTS')
        print('=' * 15)
        
        cur.execute("SELECT serial FROM motorpartsdata_serialnumber WHERE serial = 'LSFAL11A4PA157987'")
        serial = cur.fetchone()
        if serial:
            serial_id = None
            cur.execute("SELECT id FROM motorpartsdata_serialnumber WHERE serial = 'LSFAL11A4PA157987'")
            serial_id = cur.fetchone()['id']
            
            for table in ['motorpartsdata_parenttitle', 'motorpartsdata_childtitle', 'motorpartsdata_part']:
                cur.execute(f"SELECT COUNT(*) as count FROM {table} WHERE serial_number_id = %s", (serial_id,))
                count = cur.fetchone()['count']
                print(f"   {table}: {count} records")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Database error: {e}")

if __name__ == '__main__':
    main()
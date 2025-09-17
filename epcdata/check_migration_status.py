#!/usr/bin/env python
"""
Check migration status safely on server
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from django.core.management import call_command
from django.db import connection

def main():
    print("=" * 60)
    print("🔍 MIGRATION STATUS CHECK")
    print("=" * 60)
    
    # Check current migrations
    print("\n📋 Current migration status:")
    try:
        call_command('showmigrations', 'motorpartsdata', verbosity=2)
    except Exception as e:
        print(f"Error checking migrations: {e}")
    
    print("\n🗄️ Database table structure check:")
    
    # Check if oscar_imported columns exist
    cursor = connection.cursor()
    try:
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'motorpartsdata_part' 
            AND column_name IN ('oscar_imported', 'oscar_imported_at')
        """)
        
        columns = cursor.fetchall()
        print(f"Found oscar_imported columns: {columns}")
        
        if not columns:
            print("❌ oscar_imported columns are missing")
        else:
            print("✅ oscar_imported columns exist")
            
    except Exception as e:
        print(f"Error checking columns: {e}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
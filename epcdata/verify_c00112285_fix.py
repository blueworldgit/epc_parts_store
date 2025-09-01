#!/usr/bin/env python3
"""
Quick verification script to check if C00112285 pricing data sync was successful
"""

import os
import sys
import django
import psycopg2
from decimal import Decimal

# Add the project directory to Python path
sys.path.append('/home/rentals/epc_parts_store')
sys.path.append('c:/pythonstuff/vansdirect/epc_parts_store')

def check_vps_connection():
    """Check VPS database connection and C00112285 status"""
    try:
        print("🔍 Checking VPS database for C00112285...")
        
        vps_conn = psycopg2.connect(
            host="80.95.207.42",
            database="parts_store",
            user="postgres",
            password="N0rwich!"
        )
        vps_cursor = vps_conn.cursor()
        
        # Check if part exists in VPS
        vps_cursor.execute("""
            SELECT id, part_number, usage_name 
            FROM motorpartsdata_part 
            WHERE part_number = %s
        """, ('C00112285',))
        
        vps_part = vps_cursor.fetchone()
        
        if vps_part:
            part_id, part_number, usage_name = vps_part
            print(f"✅ VPS Part found: ID={part_id}, Number={part_number}, Name={usage_name}")
            
            # Check pricing data
            vps_cursor.execute("""
                SELECT id, cost_price, selling_price, stock_quantity 
                FROM motorpartsdata_pricingdata 
                WHERE part_id = %s
            """, (part_id,))
            
            pricing_data = vps_cursor.fetchone()
            
            if pricing_data:
                pricing_id, cost_price, selling_price, stock_qty = pricing_data
                print(f"✅ VPS Pricing found: Cost=£{cost_price}, Selling=£{selling_price}, Stock={stock_qty}")
                print("🎉 SUCCESS: C00112285 is fully synced on VPS!")
                return True
            else:
                print("❌ VPS Pricing data missing for C00112285")
                return False
        else:
            print("❌ VPS Part C00112285 not found")
            return False
            
    except Exception as e:
        print(f"❌ VPS connection error: {e}")
        return False
    finally:
        if 'vps_conn' in locals():
            vps_conn.close()

def check_local_connection():
    """Check local database connection and C00112285 status"""
    try:
        print("\n🔍 Checking LOCAL database for C00112285...")
        
        local_conn = psycopg2.connect(
            host="localhost",
            database="vansdirect",
            user="postgres",
            password="letmein123"
        )
        local_cursor = local_conn.cursor()
        
        # Check if part exists locally
        local_cursor.execute("""
            SELECT id, part_number, usage_name 
            FROM motorpartsdata_part 
            WHERE part_number = %s
        """, ('C00112285',))
        
        local_part = local_cursor.fetchone()
        
        if local_part:
            part_id, part_number, usage_name = local_part
            print(f"✅ LOCAL Part found: ID={part_id}, Number={part_number}, Name={usage_name}")
            
            # Check pricing data
            local_cursor.execute("""
                SELECT id, cost_price, selling_price, stock_quantity 
                FROM motorpartsdata_pricingdata 
                WHERE part_id = %s
            """, (part_id,))
            
            pricing_data = local_cursor.fetchone()
            
            if pricing_data:
                pricing_id, cost_price, selling_price, stock_qty = pricing_data
                print(f"✅ LOCAL Pricing found: Cost=£{cost_price}, Selling=£{selling_price}, Stock={stock_qty}")
                return True
            else:
                print("❌ LOCAL Pricing data missing for C00112285")
                return False
        else:
            print("❌ LOCAL Part C00112285 not found")
            return False
            
    except Exception as e:
        print(f"❌ LOCAL connection error: {e}")
        return False
    finally:
        if 'local_conn' in locals():
            local_conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("🔍 VERIFYING C00112285 PRICING DATA SYNC")
    print("=" * 60)
    
    local_ok = check_local_connection()
    vps_ok = check_vps_connection()
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"LOCAL Database: {'✅ OK' if local_ok else '❌ ISSUES'}")
    print(f"VPS Database:   {'✅ OK' if vps_ok else '❌ ISSUES'}")
    
    if local_ok and vps_ok:
        print("\n🎉 SUCCESS: C00112285 is properly synced on both databases!")
        print("💡 The part should now be visible and purchasable on your VPS website.")
    elif vps_ok:
        print("\n✅ VPS is working! The sync was successful.")
        print("💡 C00112285 should now be available on your VPS website.")
    else:
        print("\n❌ There are still sync issues. Check the logs for more details.")

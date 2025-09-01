#!/usr/bin/env python3
"""
Debug script to investigate C00112285 stock issue
Part exists in Oscar but shows 0 stock
"""

import os
import sys
import psycopg2
from decimal import Decimal

def check_vps_stock_details():
    """Check detailed stock information for C00112285 on VPS"""
    try:
        print("🔍 Checking VPS stock details for C00112285...")
        
        vps_conn = psycopg2.connect(
            host="80.95.207.42",
            database="parts_store",
            user="postgres",
            password="N0rwich!"
        )
        vps_cursor = vps_conn.cursor()
        
        # Check motorpartsdata tables
        print("\n📦 MOTORPARTSDATA TABLES:")
        print("-" * 50)
        
        # Check part exists
        vps_cursor.execute("""
            SELECT id, part_number, usage_name 
            FROM motorpartsdata_part 
            WHERE part_number = %s
        """, ('C00112285',))
        
        part_data = vps_cursor.fetchone()
        if part_data:
            part_id, part_number, usage_name = part_data
            print(f"✅ Part found: ID={part_id}, Number={part_number}")
            print(f"   Usage: {usage_name}")
            
            # Check pricing data
            vps_cursor.execute("""
                SELECT id, cost_price, selling_price, stock_quantity, created_at, updated_at
                FROM motorpartsdata_pricingdata 
                WHERE part_id = %s
            """, (part_id,))
            
            pricing_data = vps_cursor.fetchone()
            if pricing_data:
                pricing_id, cost_price, selling_price, stock_qty, created_at, updated_at = pricing_data
                print(f"✅ Pricing found: Cost=£{cost_price}, Selling=£{selling_price}")
                print(f"   Stock Quantity: {stock_qty}")
                print(f"   Created: {created_at}, Updated: {updated_at}")
            else:
                print("❌ No pricing data found")
                
        else:
            print("❌ Part not found in motorpartsdata_part")
            return
            
        # Check Oscar tables
        print("\n🏪 OSCAR TABLES:")
        print("-" * 50)
        
        # Check if product exists in Oscar
        vps_cursor.execute("""
            SELECT id, upc, title, structure
            FROM catalogue_product 
            WHERE upc = %s
        """, ('EPC-C00112285',))
        
        oscar_product = vps_cursor.fetchone()
        if oscar_product:
            oscar_id, upc, title, structure = oscar_product
            print(f"✅ Oscar Product found: ID={oscar_id}, UPC={upc}")
            print(f"   Title: {title}")
            print(f"   Structure: {structure}")
            
            # Check stock records
            vps_cursor.execute("""
                SELECT id, product_id, partner_sku, price_excl_tax, price_retail, num_in_stock, num_allocated
                FROM partner_stockrecord 
                WHERE partner_sku = %s
            """, ('C00112285',))
            
            stock_records = vps_cursor.fetchall()
            if stock_records:
                print(f"✅ Found {len(stock_records)} stock record(s):")
                for i, (stock_id, prod_id, sku, price_excl, price_retail, num_stock, num_alloc) in enumerate(stock_records, 1):
                    print(f"   Record {i}: ID={stock_id}, Product_ID={prod_id}")
                    print(f"   SKU={sku}, Price_Excl=£{price_excl}, Price_Retail=£{price_retail}")
                    print(f"   Stock={num_stock}, Allocated={num_alloc}")
            else:
                print("❌ No stock records found in partner_stockrecord")
                
            # Check product attributes
            vps_cursor.execute("""
                SELECT pa.code, pav.value_text, pav.value_integer, pav.value_float
                FROM catalogue_productattributevalue pav
                JOIN catalogue_productattribute pa ON pav.attribute_id = pa.id
                WHERE pav.product_id = %s
            """, (oscar_id,))
            
            attributes = vps_cursor.fetchall()
            if attributes:
                print(f"✅ Product has {len(attributes)} attribute(s):")
                for code, text_val, int_val, float_val in attributes:
                    value = text_val or int_val or float_val or "NULL"
                    print(f"   {code}: {value}")
            else:
                print("ℹ️ No product attributes found")
                
        else:
            print("❌ Product not found in Oscar catalogue_product")
            
        # Check if there are any partner records
        print("\n👥 PARTNER INFO:")
        print("-" * 50)
        vps_cursor.execute("""
            SELECT id, name 
            FROM partner_partner 
            ORDER BY id
        """)
        partners = vps_cursor.fetchall()
        print(f"Found {len(partners)} partner(s):")
        for partner_id, name in partners:
            print(f"   Partner {partner_id}: {name}")
            
    except Exception as e:
        print(f"❌ Error checking VPS: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'vps_conn' in locals():
            vps_conn.close()

def fix_stock_quantity():
    """Attempt to fix stock quantity for C00112285"""
    try:
        print("\n🔧 ATTEMPTING STOCK FIX:")
        print("-" * 50)
        
        vps_conn = psycopg2.connect(
            host="80.95.207.42",
            database="parts_store",
            user="postgres",
            password="N0rwich!"
        )
        vps_cursor = vps_conn.cursor()
        
        # Get the pricing data stock quantity
        vps_cursor.execute("""
            SELECT pd.stock_quantity, p.id as part_id
            FROM motorpartsdata_pricingdata pd
            JOIN motorpartsdata_part p ON pd.part_id = p.id
            WHERE p.part_number = %s
        """, ('C00112285',))
        
        pricing_stock = vps_cursor.fetchone()
        if pricing_stock:
            stock_qty, part_id = pricing_stock
            print(f"📊 Pricing data shows stock: {stock_qty}")
            
            if stock_qty and stock_qty > 0:
                # Update the Oscar stock record
                vps_cursor.execute("""
                    UPDATE partner_stockrecord 
                    SET num_in_stock = %s, num_allocated = 0
                    WHERE partner_sku = %s
                """, (stock_qty, 'C00112285'))
                
                affected_rows = vps_cursor.rowcount
                if affected_rows > 0:
                    vps_conn.commit()
                    print(f"✅ Updated {affected_rows} stock record(s) to {stock_qty} units")
                    return True
                else:
                    print("❌ No stock records found to update")
                    return False
            else:
                print(f"❌ Pricing data shows 0 or null stock: {stock_qty}")
                return False
        else:
            print("❌ No pricing data found for C00112285")
            return False
            
    except Exception as e:
        print(f"❌ Error fixing stock: {e}")
        return False
    finally:
        if 'vps_conn' in locals():
            vps_conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("🔍 DEBUGGING C00112285 STOCK ISSUE")
    print("=" * 60)
    
    check_vps_stock_details()
    
    print("\n" + "=" * 60)
    print("🔧 STOCK FIX ATTEMPT")
    print("=" * 60)
    
    fixed = fix_stock_quantity()
    
    if fixed:
        print("\n🎉 Stock quantity updated! Try checking the website again.")
    else:
        print("\n❌ Could not fix stock automatically. Manual intervention needed.")

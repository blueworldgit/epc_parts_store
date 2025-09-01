#!/usr/bin/env python3
import psycopg2

print("🔧 Fixing C00112285 stock issue...")

try:
    # Connect to VPS database
    conn = psycopg2.connect(
        host="80.95.207.42",
        database="parts_store",
        user="postgres", 
        password="N0rwich!"
    )
    cursor = conn.cursor()
    
    # Check current state
    print("\n📊 CURRENT STATE:")
    cursor.execute("""
        SELECT partner_sku, num_in_stock, price_excl_tax, price_retail 
        FROM partner_stockrecord 
        WHERE partner_sku = 'C00112285'
    """)
    current = cursor.fetchone()
    if current:
        sku, stock, price_excl, price_retail = current
        print(f"   Stock: {stock}, Price Excl: £{price_excl}, Price Retail: £{price_retail}")
    else:
        print("   ❌ No stock record found!")
        
    # Apply the fix based on JSON data
    print("\n🔧 APPLYING FIX:")
    cursor.execute("""
        UPDATE partner_stockrecord 
        SET num_in_stock = 1,
            num_allocated = 0,
            price_excl_tax = 7.91,
            price_retail = 7.91
        WHERE partner_sku = 'C00112285'
    """)
    
    affected = cursor.rowcount
    conn.commit()
    
    if affected > 0:
        print(f"   ✅ Updated {affected} record(s)")
        
        # Verify the fix
        print("\n✅ AFTER FIX:")
        cursor.execute("""
            SELECT partner_sku, num_in_stock, price_excl_tax, price_retail 
            FROM partner_stockrecord 
            WHERE partner_sku = 'C00112285'
        """)
        fixed = cursor.fetchone()
        if fixed:
            sku, stock, price_excl, price_retail = fixed
            print(f"   Stock: {stock}, Price Excl: £{price_excl}, Price Retail: £{price_retail}")
            print("\n🎉 SUCCESS: C00112285 should now show 1 in stock at £7.91!")
            print("🌐 Try refreshing the website: https://vanparts-direct.co.uk/dashboard/catalogue/products/2436/")
    else:
        print("   ❌ No records were updated")
        
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    if 'conn' in locals():
        conn.close()
        
print("\n" + "="*50)
print("Fix complete! Check the website again.")

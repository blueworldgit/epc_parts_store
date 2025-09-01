import psycopg2

# Simple stock check and fix for C00112285
try:
    print("Connecting to VPS database...")
    conn = psycopg2.connect(
        host="80.95.207.42",
        database="parts_store", 
        user="postgres",
        password="N0rwich!"
    )
    cursor = conn.cursor()
    
    # Check current stock in Oscar
    cursor.execute("""
        SELECT id, partner_sku, num_in_stock, price_excl_tax
        FROM partner_stockrecord 
        WHERE partner_sku = %s
    """, ('C00112285',))
    
    stock_record = cursor.fetchone()
    if stock_record:
        stock_id, sku, current_stock, price = stock_record
        print(f"Current Oscar stock: {current_stock} units, Price: £{price}")
        
        # Check pricing data table for correct stock
        cursor.execute("""
            SELECT pd.stock_quantity, pd.selling_price
            FROM motorpartsdata_pricingdata pd
            JOIN motorpartsdata_part p ON pd.part_id = p.id
            WHERE p.part_number = %s
        """, ('C00112285',))
        
        pricing_data = cursor.fetchone()
        if pricing_data:
            correct_stock, correct_price = pricing_data
            print(f"Pricing data stock: {correct_stock} units, Price: £{correct_price}")
            
            if correct_stock and correct_stock > 0:
                # Update Oscar stock record
                cursor.execute("""
                    UPDATE partner_stockrecord 
                    SET num_in_stock = %s, price_excl_tax = %s, price_retail = %s
                    WHERE partner_sku = %s
                """, (correct_stock, correct_price, correct_price, 'C00112285'))
                
                conn.commit()
                print(f"✅ FIXED: Updated stock to {correct_stock} units and price to £{correct_price}")
            else:
                print("❌ Pricing data also shows 0 stock")
        else:
            print("❌ No pricing data found")
    else:
        print("❌ No stock record found in Oscar")
        
except Exception as e:
    print(f"Error: {e}")
finally:
    if 'conn' in locals():
        conn.close()

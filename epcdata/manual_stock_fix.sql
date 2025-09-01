-- Manual SQL fix for C00112285 stock issue
-- Run this directly on the VPS database

-- First, check current state
SELECT 'CURRENT OSCAR STOCK:' as info;
SELECT partner_sku, num_in_stock, price_excl_tax, price_retail 
FROM partner_stockrecord 
WHERE partner_sku = 'C00112285';

SELECT 'PRICING DATA:' as info;
SELECT p.part_number, pd.stock_quantity, pd.cost_price, pd.selling_price
FROM motorpartsdata_pricingdata pd
JOIN motorpartsdata_part p ON pd.part_id = p.id
WHERE p.part_number = 'C00112285';

-- Fix the stock quantity and price
UPDATE partner_stockrecord 
SET num_in_stock = 1,
    num_allocated = 0,
    price_excl_tax = 7.91,
    price_retail = 7.91
WHERE partner_sku = 'C00112285';

-- Verify the fix
SELECT 'AFTER FIX:' as info;
SELECT partner_sku, num_in_stock, price_excl_tax, price_retail 
FROM partner_stockrecord 
WHERE partner_sku = 'C00112285';

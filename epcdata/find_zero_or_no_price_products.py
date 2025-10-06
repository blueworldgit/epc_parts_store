#!/usr/bin/env python
"""
Django shell script to find products with 0.00 or no price
Outputs results to: zero_or_no_price_products_YYYY-MM-DD_HHMMSS.txt
"""

import os
import sys
import django
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from motorpartsdata.models import Part, PricingData


def find_zero_or_no_price_products():
    """Find all products that have 0.00 prices or no price at all"""
    
    # Create timestamped filename
    timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
    filename = f'zero_or_no_price_products_{timestamp}.txt'
    
    print(f"🔍 Finding products with 0.00 or no price...")
    print(f"📝 Output file: {filename}")
    
    # Query for different price scenarios
    zero_price = PricingData.objects.filter(list_price=0.00)
    null_price = PricingData.objects.filter(list_price__isnull=True)
    no_pricing_data = Part.objects.filter(pricing_data__isnull=True)
    
    # Get total counts for comparison
    total_parts = Part.objects.count()
    total_pricing_records = PricingData.objects.count()
    zero_price_count = zero_price.count()
    null_price_count = null_price.count()
    no_pricing_count = no_pricing_data.count()
    
    print(f"📊 Statistics:")
    print(f"   Total Parts: {total_parts}")
    print(f"   Total PricingData records: {total_pricing_records}")
    print(f"   Products with £0.00 price: {zero_price_count}")
    print(f"   Products with NULL/missing price: {null_price_count}")
    print(f"   Parts with no pricing data at all: {no_pricing_count}")
    
    # Collect all problematic products
    problematic_products = []
    
    # Add zero price products
    for pricing_data in zero_price:
        if pricing_data.part_number:
            problematic_products.append({
                'part_number': pricing_data.part_number.part_number,
                'description': pricing_data.part_number.usage_name or 'No description',
                'price_issue': 'Zero price (£0.00)',
                'current_price': '£0.00',
                'stock': pricing_data.stock_available or 'Unknown'
            })
    
    # Add null price products
    for pricing_data in null_price:
        if pricing_data.part_number:
            problematic_products.append({
                'part_number': pricing_data.part_number.part_number,
                'description': pricing_data.part_number.usage_name or 'No description',
                'price_issue': 'NULL/Missing price',
                'current_price': 'No price',
                'stock': pricing_data.stock_available or 'Unknown'
            })
    
    # Add parts with no pricing data
    for part in no_pricing_data:
        problematic_products.append({
            'part_number': part.part_number,
            'description': part.usage_name or 'No description',
            'price_issue': 'No pricing record',
            'current_price': 'No pricing data',
            'stock': 'Unknown'
        })
    
    # Remove duplicates by part number (keep first occurrence)
    unique_products = {}
    for product in problematic_products:
        part_number = product['part_number']
        if part_number not in unique_products:
            unique_products[part_number] = product
    
    unique_count = len(unique_products)
    total_problematic = len(problematic_products)
    
    # Write results to file
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"Products with Zero (£0.00) or No Price\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"{'=' * 80}\n\n")
        
        f.write(f"SUMMARY:\n")
        f.write(f"Total Parts in database: {total_parts}\n")
        f.write(f"Total PricingData records: {total_pricing_records}\n")
        f.write(f"Products with £0.00 price: {zero_price_count}\n")
        f.write(f"Products with NULL/missing price: {null_price_count}\n")
        f.write(f"Parts with no pricing data: {no_pricing_count}\n")
        f.write(f"Total problematic records: {total_problematic}\n")
        f.write(f"Unique problematic parts: {unique_count}\n")
        f.write(f"Duplicate records: {total_problematic - unique_count}\n\n")
        
        # Group by issue type for better organization
        zero_price_parts = [p for p in unique_products.values() if p['price_issue'] == 'Zero price (£0.00)']
        null_price_parts = [p for p in unique_products.values() if p['price_issue'] == 'NULL/Missing price']
        no_data_parts = [p for p in unique_products.values() if p['price_issue'] == 'No pricing record']
        
        # Write zero price products
        if zero_price_parts:
            f.write(f"PRODUCTS WITH ZERO PRICE (£0.00) - {len(zero_price_parts)} parts:\n")
            f.write(f"{'Part Number':<20} {'Description':<50} {'Stock':<15}\n")
            f.write(f"{'-' * 85}\n")
            for product in sorted(zero_price_parts, key=lambda x: x['part_number']):
                description = product['description'][:45] + '...' if len(product['description']) > 45 else product['description']
                f.write(f"{product['part_number']:<20} {description:<50} {product['stock']:<15}\n")
            f.write(f"\n")
        
        # Write null price products
        if null_price_parts:
            f.write(f"PRODUCTS WITH NULL/MISSING PRICE - {len(null_price_parts)} parts:\n")
            f.write(f"{'Part Number':<20} {'Description':<50} {'Stock':<15}\n")
            f.write(f"{'-' * 85}\n")
            for product in sorted(null_price_parts, key=lambda x: x['part_number']):
                description = product['description'][:45] + '...' if len(product['description']) > 45 else product['description']
                f.write(f"{product['part_number']:<20} {description:<50} {product['stock']:<15}\n")
            f.write(f"\n")
        
        # Write parts with no pricing data
        if no_data_parts:
            f.write(f"PARTS WITH NO PRICING DATA - {len(no_data_parts)} parts:\n")
            f.write(f"{'Part Number':<20} {'Description':<50}\n")
            f.write(f"{'-' * 70}\n")
            for product in sorted(no_data_parts, key=lambda x: x['part_number']):
                description = product['description'][:45] + '...' if len(product['description']) > 45 else product['description']
                f.write(f"{product['part_number']:<20} {description:<50}\n")
            f.write(f"\n")
        
        if unique_count == 0:
            f.write("🎉 All products have valid prices!\n")
        
        f.write(f"{'=' * 80}\n")
        f.write(f"End of report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    print(f"✅ Report saved to: {filename}")
    
    # Show sample of results in console
    if unique_count > 0:
        print(f"\n📋 Sample of problematic products (showing first 10):")
        sample_products = sorted(unique_products.values(), key=lambda x: x['part_number'])[:10]
        for i, product in enumerate(sample_products, 1):
            description = product['description'][:30] + '...' if len(product['description']) > 30 else product['description']
            print(f"   {i:2d}. {product['part_number']} - {description} ({product['price_issue']})")
        
        if unique_count > 10:
            print(f"   ... and {unique_count - 10} more products (see full list in {filename})")
        
        print(f"\n💡 BREAKDOWN BY ISSUE TYPE:")
        print(f"   Zero price (£0.00): {len(zero_price_parts)} parts")
        print(f"   NULL/Missing price: {len(null_price_parts)} parts")
        print(f"   No pricing data: {len(no_data_parts)} parts")
    else:
        print(f"🎉 All {total_parts} products have valid prices!")
    
    return filename, unique_count, len(zero_price_parts), len(null_price_parts), len(no_data_parts)


def find_products_by_price_criteria(min_price=None, max_price=None, include_null=True, include_zero=True):
    """Find products based on specific price criteria"""
    
    criteria = []
    if min_price is not None:
        criteria.append(f"min_price >= £{min_price}")
    if max_price is not None:
        criteria.append(f"max_price <= £{max_price}")
    if include_null:
        criteria.append("include NULL prices")
    if include_zero:
        criteria.append("include £0.00 prices")
    
    criteria_str = ", ".join(criteria)
    print(f"🔍 Searching for products with criteria: {criteria_str}")
    
    # Build query
    query_conditions = []
    
    if include_zero:
        query_conditions.append(PricingData.objects.filter(list_price=0.00))
    
    if include_null:
        query_conditions.append(PricingData.objects.filter(list_price__isnull=True))
    
    if min_price is not None and max_price is not None:
        query_conditions.append(PricingData.objects.filter(list_price__gte=min_price, list_price__lte=max_price))
    elif min_price is not None:
        query_conditions.append(PricingData.objects.filter(list_price__gte=min_price))
    elif max_price is not None:
        query_conditions.append(PricingData.objects.filter(list_price__lte=max_price))
    
    # Combine queries
    if not query_conditions:
        print("❌ No valid search criteria provided")
        return
    
    # Union all conditions
    result_set = query_conditions[0]
    for condition in query_conditions[1:]:
        result_set = result_set.union(condition)
    
    count = result_set.count()
    print(f"📊 Found {count} pricing records matching criteria")
    
    return result_set


if __name__ == "__main__":
    try:
        filename, unique_count, zero_count, null_count, no_data_count = find_zero_or_no_price_products()
        
        print(f"\n🎯 SUMMARY:")
        print(f"   Report file: {filename}")
        print(f"   Total problematic products: {unique_count}")
        print(f"   - Zero price products: {zero_count}")
        print(f"   - NULL/Missing price: {null_count}")
        print(f"   - No pricing data: {no_data_count}")
        
        if unique_count > 0:
            print(f"\n💡 NEXT STEPS:")
            print(f"   1. Review the products in {filename}")
            print(f"   2. Update prices via Excel import or manual entry")
            print(f"   3. Run: python manage.py update_prices_from_excel [excel_file]")
            print(f"   4. Re-run this script to verify fixes")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
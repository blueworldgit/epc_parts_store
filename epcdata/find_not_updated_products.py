#!/usr/bin/env python
"""
Django shell script to find products not updated via Excel pricing
Outputs results to: notupdatedwithexcel_YYYY-MM-DD_HHMMSS.txt
"""

import os
import sys
import django
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from motorpartsdata.models import Part, PricingData


def find_products_not_updated_with_excel():
    """Find all products that haven't been updated via Excel import"""
    
    # Create timestamped filename
    timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
    filename = f'notupdatedwithexcel_{timestamp}.txt'
    
    print(f"🔍 Finding products not updated via Excel...")
    print(f"📝 Output file: {filename}")
    
    # Query for products not updated via Excel
    not_updated_pricing = PricingData.objects.filter(price_updated=False)
    
    # Get total counts for comparison
    total_pricing_records = PricingData.objects.count()
    updated_count = PricingData.objects.filter(price_updated=True).count()
    not_updated_count = not_updated_pricing.count()
    
    print(f"📊 Statistics:")
    print(f"   Total PricingData records: {total_pricing_records}")
    print(f"   Updated via Excel: {updated_count}")
    print(f"   NOT updated via Excel: {not_updated_count}")
    
    # Write results to file
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"Products NOT Updated via Excel Import\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"{'=' * 60}\n\n")
        
        f.write(f"SUMMARY:\n")
        f.write(f"Total PricingData records: {total_pricing_records}\n")
        f.write(f"Updated via Excel: {updated_count}\n")
        f.write(f"NOT updated via Excel: {not_updated_count}\n")
        f.write(f"Percentage not updated: {(not_updated_count/total_pricing_records*100):.1f}%\n\n")
        
        # Remove duplicates by grouping by part number
        unique_parts = {}
        for pricing_data in not_updated_pricing:
            part = pricing_data.part_number
            if part:
                part_number = part.part_number
                if part_number not in unique_parts:
                    unique_parts[part_number] = {
                        'part': part,
                        'pricing_data': pricing_data,
                        'usage_name': part.usage_name,
                        'current_price': pricing_data.list_price or 'No price',
                        'stock': pricing_data.stock_available or 'Unknown'
                    }
        
        unique_count = len(unique_parts)
        
        f.write(f"UNIQUE PARTS NOT UPDATED:\n")
        f.write(f"Total unique part numbers: {unique_count}\n")
        f.write(f"Total duplicate records: {not_updated_count - unique_count}\n\n")
        f.write(f"{'Part Number':<20} {'Description':<40} {'Current Price':<15} {'Stock Available':<15}\n")
        f.write(f"{'-' * 90}\n")
        
        if unique_count == 0:
            f.write("🎉 All products have been updated via Excel import!\n")
        else:
            # Sort by part number for easier reading
            for part_number in sorted(unique_parts.keys()):
                part_data = unique_parts[part_number]
                usage_name = part_data['usage_name'][:35] + '...' if len(part_data['usage_name']) > 35 else part_data['usage_name']
                
                f.write(f"{part_number:<20} {usage_name:<40} {part_data['current_price']:<15} {part_data['stock']:<15}\n")
        
        f.write(f"\n{'=' * 60}\n")
        f.write(f"End of report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    print(f"✅ Report saved to: {filename}")
    
    # Remove duplicates for console display
    unique_parts = {}
    for pricing_data in not_updated_pricing:
        part = pricing_data.part_number
        if part:
            part_number = part.part_number
            if part_number not in unique_parts:
                unique_parts[part_number] = {
                    'part': part,
                    'pricing_data': pricing_data,
                    'usage_name': part.usage_name,
                    'price': pricing_data.list_price or 'No price'
                }
    
    unique_count = len(unique_parts)
    
    # Show sample of results in console
    if not_updated_count > 0:
        print(f"\n� DUPLICATES ANALYSIS:")
        print(f"   Total records not updated: {not_updated_count}")
        print(f"   Unique part numbers: {unique_count}")
        print(f"   Duplicate records: {not_updated_count - unique_count}")
        
        print(f"\n📋 Sample of unique parts not updated (showing first 5):")
        for i, (part_number, part_data) in enumerate(sorted(unique_parts.items())[:5]):
            usage_name = part_data['usage_name']
            price = part_data['price']
            print(f"   {i+1}. {part_number} - {usage_name} (£{price})")
        
        if unique_count > 5:
            print(f"   ... and {unique_count - 5} more unique parts (see full list in {filename})")
    else:
        print(f"🎉 All {total_pricing_records} products have been updated via Excel!")
    
    return filename, unique_count


if __name__ == "__main__":
    try:
        filename, unique_count = find_products_not_updated_with_excel()
        print(f"\n🎯 SUMMARY:")
        print(f"   Report file: {filename}")
        print(f"   Unique products not updated: {unique_count}")
        
        if unique_count > 0:
            print(f"\n💡 NEXT STEPS:")
            print(f"   1. Review the unique products in {filename}")
            print(f"   2. Check if these products should be in your Excel file")
            print(f"   3. Run: python manage.py update_prices_from_excel")
            print(f"   4. Re-run this script to verify updates")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
#!/usr/bin/env python
"""
Custom script to update Oscar stock records from existing PricingData
This script reads from your motorpartsdata models and updates Oscar StockRecord num_in_stock
Usage: python update_stock.py
"""

import os
import sys
import django
from decimal import Decimal, InvalidOperation
import logging

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from motorpartsdata.models import Part, PricingData
from oscar.apps.partner.models import StockRecord, Partner

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('stock_update.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def parse_stock_value(stock_str):
    """
    Parse stock_available string into integer
    Rules:
    - '10+' becomes 12
    - 'Nil' or '0' becomes 0
    - Regular numbers stay as is
    """
    if not stock_str:
        return 0
    
    stock_str = str(stock_str).strip()
    
    # Handle 'Nil' case
    if stock_str.lower() == 'nil' or stock_str == '0':
        return 0
    
    # Handle '10+' case - set to 12 as requested
    if stock_str.endswith('+'):
        try:
            base_num = int(stock_str.replace('+', ''))
            return base_num + 2  # Add 2 to the base number (10+ becomes 12)
        except ValueError:
            logger.warning(f"Could not parse '+' value: {stock_str}, defaulting to 12")
            return 12
    
    # Handle regular numbers
    try:
        return int(float(stock_str.replace(',', '')))
    except (ValueError, TypeError):
        logger.warning(f"Could not parse stock value: {stock_str}, defaulting to 0")
        return 0

def update_stock_records():
    """Update all stock records with correct stock levels"""
    
    # Get the EPC partner
    try:
        partner = Partner.objects.get(name='EPC Motor Parts Store')
    except Partner.DoesNotExist:
        logger.error("EPC Motor Parts Store partner not found. Run the Oscar import first.")
        return False
    
    # Get all parts that have pricing data
    parts_with_pricing = Part.objects.filter(pricing_data__isnull=False).distinct()
    total_parts = parts_with_pricing.count()
    
    logger.info(f"Found {total_parts} parts with pricing data to process")
    
    updated_count = 0
    no_stock_record_count = 0
    error_count = 0
    
    for part in parts_with_pricing:
        try:
            # Get pricing data for this part
            try:
                pricing_data = PricingData.objects.get(part_number=part)
            except PricingData.DoesNotExist:
                logger.warning(f"No pricing data found for part {part.part_number}")
                continue
            
            # Find the corresponding stock record
            try:
                stock_record = StockRecord.objects.get(
                    partner=partner,
                    partner_sku=part.part_number
                )
            except StockRecord.DoesNotExist:
                logger.warning(f"No stock record found for part {part.part_number}")
                no_stock_record_count += 1
                continue
            
            # Parse the stock_available value and ALWAYS update (overwrite)
            new_stock_level = parse_stock_value(pricing_data.stock_available)
            old_stock = stock_record.num_in_stock
            
            stock_record.num_in_stock = new_stock_level
            stock_record.save()
            
            logger.info(f"Updated {part.part_number}: {old_stock} → {new_stock_level} (from '{pricing_data.stock_available}')")
            updated_count += 1
                
        except Exception as e:
            logger.error(f"Error updating stock for part {part.part_number}: {str(e)}")
            error_count += 1
    
    # Print summary
    logger.info("=== Stock Update Summary ===")
    logger.info(f"Total parts with pricing: {total_parts}")
    logger.info(f"Updated: {updated_count}")
    logger.info(f"No stock record: {no_stock_record_count}")
    logger.info(f"Errors: {error_count}")
    
    return error_count == 0

def show_sample_data():
    """Show sample of current stock data for verification"""
    logger.info("=== Sample Current Data ===")
    
    # Show some pricing data examples
    pricing_samples = PricingData.objects.exclude(stock_available__isnull=True).exclude(stock_available='')[:5]
    for pricing in pricing_samples:
        part_number = pricing.part_number.part_number
        original_stock = pricing.stock_available
        parsed_stock = parse_stock_value(original_stock)
        
        logger.info(f"Part {part_number}: '{original_stock}' → {parsed_stock}")
    
    # Show some stock record examples
    stock_samples = StockRecord.objects.all()[:5]
    for stock in stock_samples:
        logger.info(f"Stock Record {stock.partner_sku}: current stock = {stock.num_in_stock}")

def main():
    """Main function"""
    logger.info("Starting stock level update from PricingData...")
    
    # Show sample data first
    show_sample_data()
    
    # Ask for confirmation
    if len(sys.argv) > 1 and sys.argv[1] == '--force':
        proceed = True
    else:
        try:
            response = input("\nProceed with stock update? (y/N): ").strip().lower()
            proceed = response in ['y', 'yes']
        except KeyboardInterrupt:
            logger.info("Update cancelled by user")
            return
    
    if not proceed:
        logger.info("Update cancelled")
        return
    
    # Perform the update
    success = update_stock_records()
    
    if success:
        logger.info("Stock update completed successfully!")
    else:
        logger.error("Stock update completed with errors. Check the log file for details.")

if __name__ == "__main__":
    main()

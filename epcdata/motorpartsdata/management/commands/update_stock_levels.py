#!/usr/bin/env python
"""
Django management command to update stock levels from PricingData
Usage: python manage.py update_stock_levels [--dry-run]
"""

from django.core.management.base import BaseCommand
from django.db import transaction
import logging

from motorpartsdata.models import Part, PricingData
from oscar.apps.partner.models import StockRecord, Partner

class Command(BaseCommand):
    help = 'Update Oscar stock records from PricingData models'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes',
        )
    
    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No changes will be made')
            )
        
        # Get the EPC partner
        try:
            partner = Partner.objects.get(name='EPC Motor Parts Store')
        except Partner.DoesNotExist:
            self.stderr.write("EPC Motor Parts Store partner not found. Run the Oscar import first.")
            return
        
        # Statistics
        stats = {
            'total': 0,
            'updated': 0,
            'no_pricing': 0,
            'no_stock_record': 0,
            'errors': 0
        }
        
        # Process ALL parts with pricing data
        parts_with_pricing = Part.objects.filter(pricing_data__isnull=False).distinct()
        stats['total'] = parts_with_pricing.count()
        
        self.stdout.write(f"Processing {stats['total']} parts with pricing data...")
        
        try:
            with transaction.atomic():
                for part in parts_with_pricing:
                    try:
                        # Get pricing data for this part
                        try:
                            pricing_data = PricingData.objects.get(part_number=part)
                        except PricingData.DoesNotExist:
                            stats['no_pricing'] += 1
                            continue
                        
                        # Find the corresponding stock record
                        try:
                            stock_record = StockRecord.objects.get(
                                partner=partner,
                                partner_sku=part.part_number
                            )
                        except StockRecord.DoesNotExist:
                            if options['verbosity'] >= 2:
                                self.stdout.write(f"No stock record for {part.part_number}")
                            stats['no_stock_record'] += 1
                            continue
                        
                        # Parse stock value and ALWAYS update (overwrite)
                        new_stock = self._parse_stock_value(pricing_data.stock_available)
                        old_stock = stock_record.num_in_stock
                        
                        if not dry_run:
                            stock_record.num_in_stock = new_stock
                            stock_record.save()
                        
                        self.stdout.write(
                            f"{'[DRY RUN] ' if dry_run else ''}Updated {part.part_number}: "
                            f"{old_stock} → {new_stock} (from '{pricing_data.stock_available}')"
                        )
                        stats['updated'] += 1
                            
                    except Exception as e:
                        self.stderr.write(f"Error processing {stock_record.partner_sku}: {str(e)}")
                        stats['errors'] += 1
                
                if dry_run:
                    # Rollback in dry run mode
                    raise transaction.TransactionManagementError("Dry run - rolling back")
        
        except transaction.TransactionManagementError:
            if not dry_run:
                self.stderr.write("Transaction failed")
                return
        
        # Print summary
        self.stdout.write(self.style.SUCCESS("=== Stock Update Summary ==="))
        self.stdout.write(f"Total parts processed: {stats['total']}")
        self.stdout.write(f"Updated: {stats['updated']}")
        self.stdout.write(f"No pricing data: {stats['no_pricing']}")
        self.stdout.write(f"No stock record: {stats['no_stock_record']}")
        if stats['errors'] > 0:
            self.stdout.write(self.style.ERROR(f"Errors: {stats['errors']}"))
        
        if not dry_run and stats['updated'] > 0:
            self.stdout.write(self.style.SUCCESS("Stock levels updated successfully!"))
    
    def _parse_stock_value(self, stock_str):
        """Parse stock_available string into integer"""
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
                return base_num + 2  # 10+ becomes 12
            except ValueError:
                return 12  # Default for unparseable '+' values
        
        # Handle regular numbers
        try:
            return int(float(stock_str.replace(',', '')))
        except (ValueError, TypeError):
            return 0

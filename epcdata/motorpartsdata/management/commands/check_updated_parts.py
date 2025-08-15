from django.core.management.base import BaseCommand
from motorpartsdata.models import Part, PricingData
import os
from datetime import datetime

class Command(BaseCommand):
    help = 'Check which parts were updated and output to notupdated.txt'

    def handle(self, *args, **options):
        # Get the base directory for output file
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        output_file_path = os.path.join(base_dir, 'notupdated.txt')
        
        self.stdout.write(f"Checking all parts and their update status...")
        self.stdout.write(f"Output will be saved to: {output_file_path}")
        
        # Get all parts
        all_parts = Part.objects.all()
        total_parts = all_parts.count()
        
        updated_count = 0
        not_updated_count = 0
        no_pricing_data_count = 0
        
        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            output_file.write(f"Parts Update Status Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            output_file.write("=" * 80 + "\n\n")
            output_file.write(f"Total parts in database: {total_parts}\n\n")
            
            output_file.write("PARTS THAT WERE UPDATED:\n")
            output_file.write("-" * 40 + "\n")
            
            # First pass - find updated parts
            for part in all_parts:
                try:
                    pricing_data = PricingData.objects.get(part_number=part)
                    if pricing_data.price_updated:
                        updated_count += 1
                        output_file.write(f"SKU: {part.part_number} - UPDATED (Price: £{pricing_data.list_price})\n")
                except PricingData.DoesNotExist:
                    # Will handle this in the next section
                    pass
            
            output_file.write(f"\nTotal UPDATED parts: {updated_count}\n\n")
            
            output_file.write("PARTS THAT WERE NOT UPDATED:\n")
            output_file.write("-" * 40 + "\n")
            
            # Second pass - find not updated parts
            for part in all_parts:
                try:
                    pricing_data = PricingData.objects.get(part_number=part)
                    if not pricing_data.price_updated:
                        not_updated_count += 1
                        price_display = pricing_data.list_price if pricing_data.list_price else "No price"
                        output_file.write(f"SKU: {part.part_number} - NOT UPDATED (Price: {price_display})\n")
                except PricingData.DoesNotExist:
                    no_pricing_data_count += 1
                    output_file.write(f"SKU: {part.part_number} - NO PRICING DATA\n")
            
            output_file.write(f"\nTotal NOT UPDATED parts: {not_updated_count}\n")
            output_file.write(f"Total parts with NO PRICING DATA: {no_pricing_data_count}\n")
            
            output_file.write("\nSUMMARY:\n")
            output_file.write("-" * 20 + "\n")
            output_file.write(f"Total parts: {total_parts}\n")
            output_file.write(f"Updated: {updated_count}\n")
            output_file.write(f"Not updated: {not_updated_count}\n")
            output_file.write(f"No pricing data: {no_pricing_data_count}\n")
            output_file.write(f"Report generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Also output summary to console
        self.stdout.write(self.style.SUCCESS(f"\nSummary:"))
        self.stdout.write(f"Total parts: {total_parts}")
        self.stdout.write(self.style.SUCCESS(f"Updated: {updated_count}"))
        self.stdout.write(self.style.WARNING(f"Not updated: {not_updated_count}"))
        self.stdout.write(self.style.ERROR(f"No pricing data: {no_pricing_data_count}"))
        self.stdout.write(f"\nDetailed report saved to: {output_file_path}")

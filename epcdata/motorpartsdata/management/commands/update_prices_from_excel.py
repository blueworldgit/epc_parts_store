from django.core.management.base import BaseCommand
from django.db import transaction
from motorpartsdata.models import Part, PricingData, PriceUpdateTracker
import openpyxl
import os
from datetime import datetime

class Command(BaseCommand):
    help = 'Update parts prices from PRCJUL25.xlsx.'

    def handle(self, *args, **options):
        # The project's base directory, where manage.py is located, is the parent of the app directory.
        # This command is in motorpartsdata/management/commands. We go up 4 levels to get to the project root.
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        file_path = os.path.join(base_dir, 'PRCJUL25.xlsx')
        
        self.stdout.write(f"Attempting to open workbook at: {file_path}")

        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"Error: The file was not found at the specified path."))
            return

        try:
            workbook = openpyxl.load_workbook(file_path)
            sheet = workbook.active
            self.stdout.write("Workbook loaded successfully.")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred while opening the workbook: {e}"))
            return

        # Process each row in its own transaction to avoid transaction errors
        successful_updates = 0
        failed_updates = 0
        
        # Create output log file
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        log_file_path = os.path.join(base_dir, 'priceupdate.txt')
        
        with open(log_file_path, 'w', encoding='utf-8') as log_file:
            log_file.write(f"Price Update Log - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            log_file.write("=" * 60 + "\n\n")
            
            self.stdout.write(f"Processing all rows in Excel file...")
            self.stdout.write(f"Logging results to: {log_file_path}")
            
            # Skip the header row (min_row=2) and read values directly - process ALL rows
            for row_num, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
                sku = row[0]  # Part Number (column A)
                description = row[1]  # Description (column B)
                price = row[5]  # Retail Price (column F)

                # Skip rows where SKU is missing or price is None/empty
                if not sku or price is None:
                    continue

                try:
                    with transaction.atomic():
                        # Find all parts with the matching SKU (handle duplicates)
                        parts = Part.objects.filter(part_number=sku)
                        
                        if not parts.exists():
                            raise Part.DoesNotExist(f"No parts found with SKU: {sku}")
                        
                        parts_updated = 0
                        for part in parts:
                            # Get or create the pricing data for this part
                            pricing_data, created = PricingData.objects.get_or_create(part_number=part)
                            
                            # Update the price and related fields
                            old_price = pricing_data.list_price
                            pricing_data.list_price = str(price)  # Convert to string as model expects
                            pricing_data.description = description if description else pricing_data.description
                            pricing_data.price_updated = True  # Now this field exists in the database
                            pricing_data.save()
                            parts_updated += 1

                        successful_updates += 1
                        success_msg = f"Updated {parts_updated} parts with SKU: {sku} to £{price}"
                        self.stdout.write(self.style.SUCCESS(success_msg))
                        log_file.write(f"SUCCESS: {success_msg}\n")

                except Part.DoesNotExist:
                    failed_updates += 1
                    warning_msg = f"SKU not found in Part model: {sku}"
                    self.stdout.write(self.style.WARNING(warning_msg))
                    log_file.write(f"WARNING: {warning_msg}\n")
                except Exception as e:
                    failed_updates += 1
                    error_msg = f"An error occurred processing SKU {sku}: {e}"
                    self.stdout.write(self.style.ERROR(error_msg))
                    log_file.write(f"ERROR: {error_msg}\n")

            # Final summary
            summary_msg = f"\nUpdate completed: {successful_updates} successful, {failed_updates} failed"
            self.stdout.write(self.style.SUCCESS(summary_msg))
            log_file.write(f"\n{summary_msg}\n")
            log_file.write(f"Log completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

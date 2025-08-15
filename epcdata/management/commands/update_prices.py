from django.core.management.base import BaseCommand
import openpyxl
from epcdata.motorpartsdata.models import Part, PricingData
import os

class Command(BaseCommand):
    help = 'Update parts prices from an Excel file.'

    def handle(self, *args, **options):
        file_path = os.path.join('epcdata', 'PRCJUL25.xlsx')
        self.stdout.write(f"Opening workbook: {file_path}")

        try:
            workbook = openpyxl.load_workbook(file_path)
            sheet = workbook.active
            self.stdout.write("Workbook loaded successfully.")
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"Error: The file '{file_path}' was not found."))
            return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred while opening the workbook: {e}"))
            return

        for row in sheet.iter_rows(min_row=2, values_only=True):
            sku = row[0]
            price = row[1]

            if not sku:
                continue

            try:
                part = Part.objects.get(part_number=sku)
                pricing_data, created = PricingData.objects.get_or_create(part_number=part)
                
                pricing_data.list_price = price
                pricing_data.price_updated = True
                pricing_data.save()

                self.stdout.write(self.style.SUCCESS(f"Updated price for SKU: {sku}"))

            except Part.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"SKU not found: {sku}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"An error occurred processing SKU {sku}: {e}"))

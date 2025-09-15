from django.core.management.base import BaseCommand
import pandas as pd
import numpy as np
from motorpartsdata.models import Part, PricingData
from oscar.apps.catalogue.models import Product
from oscar.apps.partner.models import StockRecord
from decimal import Decimal, InvalidOperation
import os

class Command(BaseCommand):
    help = 'Update parts prices from an Excel file (with enhanced debugging).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output'
        )
        parser.add_argument(
            '--debug',
            action='store_true',
            help='Show extensive debugging information'
        )
        parser.add_argument(
            '--sync-to-oscar',
            action='store_true',
            help='Also update Django Oscar StockRecord prices'
        )

    def handle(self, *args, **options):
        verbose = options.get('verbose', False)
        debug = options.get('debug', False)
        sync_to_oscar = options.get('sync_to_oscar', False)
        
        # Find the Excel file - it should be in the main epcdata directory
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        file_path = os.path.join(base_dir, 'PRCJUL25.xlsx')
        
        # Alternative paths to check
        alt_paths = [
            os.path.join('epcdata', 'PRCJUL25.xlsx'),
            os.path.join('..', 'PRCJUL25.xlsx'),
            'PRCJUL25.xlsx'
        ]
        
        self.stdout.write("="*80)
        self.stdout.write("ENHANCED PRICE UPDATE COMMAND (DEBUG VERSION)")
        self.stdout.write("="*80)
        self.stdout.write(f"File path: {file_path}")
        self.stdout.write(f"Verbose mode: {verbose}")
        self.stdout.write(f"Debug mode: {debug}")
        self.stdout.write(f"Sync to Oscar: {sync_to_oscar}")
        self.stdout.write("")

        # Check if file exists
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"❌ File not found: {file_path}"))
            
            # Try alternative paths
            for alt_path in alt_paths:
                if os.path.exists(alt_path):
                    file_path = alt_path
                    self.stdout.write(f"✅ Found file at: {file_path}")
                    break
            else:
                # Look for Excel files in current directory and parent directories
                search_dirs = ['.', '..', 'epcdata', base_dir]
                self.stdout.write("🔍 Searching for Excel files in:")
                for search_dir in search_dirs:
                    self.stdout.write(f"  {os.path.abspath(search_dir) if os.path.exists(search_dir) else search_dir}")
                    if os.path.exists(search_dir):
                        excel_files = [f for f in os.listdir(search_dir) if f.endswith(('.xlsx', '.xls'))]
                        if excel_files:
                            self.stdout.write(f"📁 Found Excel files in {search_dir}:")
                            for f in excel_files:
                                full_path = os.path.join(search_dir, f)
                                self.stdout.write(f"  - {f} (full path: {os.path.abspath(full_path)})")
                return

        self.stdout.write(f"📂 Loading Excel file with pandas: {file_path}")

        try:
            # Load Excel file with pandas - much more robust parsing
            df = pd.read_excel(file_path, engine='openpyxl')
            
            self.stdout.write(f"✅ Excel file loaded successfully.")
            self.stdout.write(f"📊 DataFrame shape: {df.shape[0]} rows x {df.shape[1]} columns")
            self.stdout.write(f"📊 Column names: {list(df.columns)}")
            
            # Detect SKU and Price columns intelligently
            sku_col = None
            price_col = None
            
            # Try common column names for SKU
            for col in df.columns:
                col_lower = str(col).lower()
                if any(keyword in col_lower for keyword in ['sku', 'part', 'number', 'code']):
                    sku_col = col
                    break
            
            # Try common column names for Price  
            for col in df.columns:
                col_lower = str(col).lower()
                if any(keyword in col_lower for keyword in ['price', 'cost', 'amount', 'value']):
                    price_col = col
                    break
            
            # If not found, assume first two columns
            if sku_col is None:
                sku_col = df.columns[0]
                self.stdout.write(f"⚠️  SKU column not detected, using first column: '{sku_col}'")
            
            if price_col is None:
                price_col = df.columns[1] if len(df.columns) > 1 else df.columns[0]
                self.stdout.write(f"⚠️  Price column not detected, using second column: '{price_col}'")
            
            self.stdout.write(f"� Using SKU column: '{sku_col}'")
            self.stdout.write(f"📋 Using Price column: '{price_col}'")
            
            # Clean the data
            df = df.dropna(subset=[sku_col])  # Remove rows with empty SKUs
            df[sku_col] = df[sku_col].astype(str).str.strip()  # Clean SKUs
            
            # Show data preview
            if debug:
                self.stdout.write(f"\n📋 Data types:")
                for col in [sku_col, price_col]:
                    if col in df.columns:
                        self.stdout.write(f"  {col}: {df[col].dtype}")
                
                self.stdout.write(f"\n📋 First 5 rows of cleaned data:")
                preview_df = df[[sku_col, price_col]].head()
                for idx, row in preview_df.iterrows():
                    self.stdout.write(f"  Row {idx + 1}: SKU='{row[sku_col]}', Price='{row[price_col]}'")
                self.stdout.write("")
                
            # Show price column analysis
            price_series = df[price_col]
            numeric_prices = pd.to_numeric(price_series, errors='coerce')
            valid_prices = numeric_prices.notna()
            
            self.stdout.write(f"📊 Price column analysis:")
            self.stdout.write(f"  Total rows: {len(df)}")
            self.stdout.write(f"  Valid numeric prices: {valid_prices.sum()}")
            self.stdout.write(f"  Invalid/text prices: {(~valid_prices).sum()}")
            
            if debug and (~valid_prices).sum() > 0:
                invalid_samples = df[~valid_prices][[sku_col, price_col]].head(5)
                self.stdout.write(f"  Sample invalid prices:")
                for idx, row in invalid_samples.iterrows():
                    self.stdout.write(f"    SKU: {row[sku_col]}, Price: '{row[price_col]}'")
                
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"❌ File not found: {file_path}"))
            return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error loading Excel file: {e}"))
            return

        # Statistics tracking
        stats = {
            'rows_processed': 0,
            'pricing_data_updated': 0,
            'oscar_updated': 0,
            'parts_not_found': 0,
            'oscar_not_found': 0,
            'price_conversion_errors': 0,
            'text_descriptions_skipped': 0,
            'errors': 0,
        }

        self.stdout.write("🔄 Processing rows with pandas...")
        
        # Process each row in the DataFrame
        for idx, row in df.iterrows():
            row_num = idx + 2  # Add 2 for Excel row number (1-indexed + header)
            sku = str(row[sku_col]).strip()
            price = row[price_col]

            if not sku or sku.lower() in ['nan', 'none']:
                if debug:
                    self.stdout.write(f"Row {row_num}: ⚠️  Empty SKU, skipping")
                continue

            # Enhanced price validation with pandas
            if pd.isna(price) or price == '':
                if debug:
                    self.stdout.write(f"Row {row_num}: ⚠️  Empty price for {sku}, skipping")
                continue
            
            # Convert to string for text analysis
            price_str = str(price).strip()
            
            # Check if it's a numeric value first (pandas is better at this)
            if pd.api.types.is_numeric_dtype(type(price)) and not pd.isna(price):
                # It's already a number, use it directly
                numeric_price = float(price)
                if numeric_price <= 0:
                    if debug:
                        self.stdout.write(f"Row {row_num}: ⚠️  Non-positive price {numeric_price} for {sku}, skipping")
                    stats['text_descriptions_skipped'] += 1
                    continue
            else:
                # Try to convert text to numeric
                numeric_price = pd.to_numeric(price, errors='coerce')
                if pd.isna(numeric_price):
                    # Check if it's clearly a text description
                    description_keywords = ['bolt', 'nut', 'screw', 'weight', 'washer', 'gasket', 'seal', 'clip', 'bracket', 'hose', 'pipe', 'valve', 'filter', 'bearing', 'bushing', 'shaft', 'hex', 'flange']
                    if any(keyword in price_str.lower() for keyword in description_keywords):
                        if debug:
                            self.stdout.write(f"Row {row_num}: ⚠️  Text description in price column for {sku}: '{price}', skipping")
                        stats['text_descriptions_skipped'] += 1
                        continue
                    
                    # Try cleaning common price formats
                    clean_price = price_str.replace('£', '').replace('$', '').replace(',', '').replace('€', '').strip()
                    numeric_price = pd.to_numeric(clean_price, errors='coerce')
                    
                    if pd.isna(numeric_price):
                        if debug:
                            self.stdout.write(f"Row {row_num}: ⚠️  Could not convert price '{price}' for {sku}, skipping")
                        stats['text_descriptions_skipped'] += 1
                        continue
                else:
                    numeric_price = float(numeric_price)

            stats['rows_processed'] += 1
            
            if debug:
                self.stdout.write(f"\n📋 Row {row_num}: Processing SKU '{sku}', Price: {numeric_price}")

            try:
                # Update PricingData model - handle potential duplicates
                part = Part.objects.filter(part_number=sku).first()
                if not part:
                    stats['parts_not_found'] += 1
                    if verbose or debug:
                        self.stdout.write(f"  ⚠️  Part not found: {sku}")
                    continue
                    
                pricing_data, created = PricingData.objects.get_or_create(part_number=part)
                
                # Convert the validated numeric price to Decimal
                try:
                    decimal_price = Decimal(str(numeric_price))
                    
                    old_price = pricing_data.list_price
                    pricing_data.list_price = decimal_price
                    pricing_data.price_updated = True
                    pricing_data.save()
                    
                    stats['pricing_data_updated'] += 1
                    action = "Created" if created else "Updated"
                    
                    if verbose or debug:
                        self.stdout.write(f"  ✅ {action} PricingData: {old_price} → {decimal_price}")
                        
                except (ValueError, TypeError, InvalidOperation) as price_error:
                    stats['price_conversion_errors'] += 1
                    self.stdout.write(f"  ❌ PricingData price conversion error for {sku}: '{numeric_price}' -> {type(price_error).__name__}")
                    continue

                # Also update Django Oscar StockRecord if requested
                if sync_to_oscar:
                    try:
                        # Find matching Oscar product
                        oscar_product = Product.objects.filter(upc=sku).first()
                        if oscar_product:
                            stock_record = StockRecord.objects.filter(product=oscar_product).first()
                            if stock_record:
                                old_oscar_price = stock_record.price
                                
                                # Use the already validated numeric price
                                try:
                                    oscar_decimal_price = Decimal(str(numeric_price))
                                    
                                    stock_record.price = oscar_decimal_price
                                    stock_record.save()
                                    
                                    # Verify save
                                    stock_record.refresh_from_db()
                                    if stock_record.price == oscar_decimal_price:
                                        stats['oscar_updated'] += 1
                                        if verbose or debug:
                                            self.stdout.write(f"  ✅ Updated Oscar StockRecord: £{old_oscar_price} → £{stock_record.price}")
                                    else:
                                        self.stdout.write(f"  ❌ Oscar save verification failed for {sku}: expected £{oscar_decimal_price}, got £{stock_record.price}")
                                        
                                except (ValueError, TypeError, InvalidOperation) as price_error:
                                    stats['price_conversion_errors'] += 1
                                    self.stdout.write(f"  ❌ Oscar price conversion error for {sku}: '{numeric_price}' -> {type(price_error).__name__}")
                                
                            else:
                                stats['oscar_not_found'] += 1
                                if debug:
                                    self.stdout.write(f"  ⚠️  No Oscar StockRecord found for {sku}")
                        else:
                            stats['oscar_not_found'] += 1
                            if debug:
                                self.stdout.write(f"  ⚠️  No Oscar Product found for UPC {sku}")
                    except Exception as oscar_error:
                        self.stdout.write(f"  ❌ Oscar update error for {sku}: {type(oscar_error).__name__}: {oscar_error}")
                        if debug:
                            import traceback
                            self.stdout.write(f"     Full traceback: {traceback.format_exc()}")

                if not debug and stats['rows_processed'] % 50 == 0:
                    self.stdout.write(f"  Processed {stats['rows_processed']} rows...")

            except Exception as e:
                stats['errors'] += 1
                self.stdout.write(f"  ❌ Error processing {sku}: {e}")
                if debug:
                    import traceback
                    self.stdout.write(f"     Full traceback: {traceback.format_exc()}")

        # Final statistics
        self.stdout.write("\n" + "="*60)
        self.stdout.write("ENHANCED SUMMARY")
        self.stdout.write("="*60)
        self.stdout.write(f"File: {file_path}")
        self.stdout.write(f"Rows processed: {stats['rows_processed']}")
        self.stdout.write(f"PricingData updated: {stats['pricing_data_updated']}")
        if sync_to_oscar:
            self.stdout.write(f"Oscar StockRecords updated: {stats['oscar_updated']}")
            self.stdout.write(f"Oscar products not found: {stats['oscar_not_found']}")
            self.stdout.write(f"Price conversion errors: {stats['price_conversion_errors']}")
        self.stdout.write(f"Parts not found: {stats['parts_not_found']}")
        self.stdout.write(f"Text descriptions skipped: {stats['text_descriptions_skipped']}")
        self.stdout.write(f"Errors: {stats['errors']}")
        
        if not sync_to_oscar:
            self.stdout.write("")
            self.stdout.write("⚠️  NOTE: Only PricingData was updated, not Oscar StockRecords!")
            self.stdout.write("   Use --sync-to-oscar flag to also update prices displayed on website")
            self.stdout.write("")
            self.stdout.write("   To sync prices to Oscar:")
            self.stdout.write("   python manage.py update_prices --sync-to-oscar")
        else:
            if stats['price_conversion_errors'] > 0:
                self.stdout.write("")
                self.stdout.write(f"⚠️  {stats['price_conversion_errors']} prices had conversion errors (text values, invalid formats)")
                self.stdout.write("   These rows were skipped for Oscar updates but PricingData may still be updated")
                self.stdout.write("   Check your Excel file for non-numeric values in the price column")

        self.stdout.write(f"\n✅ Price update complete!")
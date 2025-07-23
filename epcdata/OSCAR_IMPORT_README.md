# Oscar Import Scripts

This package contains scripts to import your existing motorpartsdata into Django Oscar e-commerce framework. The scripts handle the complete pipeline from raw data to Oscar products with duplicate detection and pricing integration.

## Overview

The import process consists of three main steps:

1. **Parts Import** (`scrapeandpush.py`) - Import HTML files to create the Serial→ParentTitle→ChildTitle→Part hierarchy
2. **Pricing Import** (`loadprices.py`) - Import JSON pricing data and link it to existing parts
3. **Oscar Import** (`import_to_oscar.py` or Django command) - Convert the data structure to Oscar products and categories

## Scripts Available

### 1. PowerShell Script (Recommended)
**File:** `import_oscar_complete.ps1`

**Features:**
- Complete automated import process
- Error handling and validation
- Dry-run mode for testing
- Verbose output option
- Skip individual steps if needed

**Usage:**
```powershell
# Full import
.\import_oscar_complete.ps1 "C:\data\parts" "C:\data\pricing"

# Import specific serial number only
.\import_oscar_complete.ps1 "C:\data\parts" "C:\data\pricing" -Serial "LSH14C4C5NA129710"

# Dry run (test without making changes)
.\import_oscar_complete.ps1 "C:\data\parts" "C:\data\pricing" -DryRun

# Verbose output
.\import_oscar_complete.ps1 "C:\data\parts" "C:\data\pricing" -Verbose

# Skip steps if data already imported
.\import_oscar_complete.ps1 "C:\data\parts" "C:\data\pricing" -SkipParts -SkipPricing

# Only import to Oscar (if parts and pricing already done)
.\import_oscar_complete.ps1 "C:\data\parts" "C:\data\pricing" -SkipParts -SkipPricing
```

### 2. Simple Batch Script
**File:** `import_oscar_simple.bat`

**Usage:**
```batch
import_oscar_simple.bat "C:\data\parts" "C:\data\pricing"
```

### 3. Python Scripts (Manual)

#### Individual Scripts:
```bash
# Step 1: Import parts
python scrapeandpush.py "C:\data\parts"

# Step 2: Import pricing
python loadprices.py "C:\data\pricing"

# Step 3: Import to Oscar
python import_to_oscar.py
```

#### Django Management Command:
```bash
# Import all data
python manage.py import_to_oscar

# Import specific serial
python manage.py import_to_oscar --serial "LSH14C4C5NA129710"

# Dry run
python manage.py import_to_oscar --dry-run

# Verbose output
python manage.py import_to_oscar --verbose -v 2
```

## Data Structure Mapping

### Original Structure → Oscar Structure

```
SerialNumber                 → Root Category
├── ParentTitle             → Parent Category  
    ├── ChildTitle          → Child Category
        ├── Part            → Product
        └── PricingData     → StockRecord
```

### Oscar Products Include:
- **Product Title:** `{part_number} - {usage_name}`
- **UPC/SKU:** `EPC-{part_number}`
- **Categories:** Hierarchical based on Serial→Parent→Child
- **Attributes:**
  - Part Number
  - Call Out Order
  - Unit Quantity
  - L/R Orientation
  - Remark
  - NN Note
  - SVG Diagram (from ChildTitle)

### Stock Records Include:
- **Price:** Extracted from PricingData.list_price
- **Stock Level:** Extracted from PricingData.stock_available
- **Partner SKU:** Part number
- **Currency:** GBP

## Duplicate Detection

All scripts include duplicate detection:

- **Parts Import:** Checks for existing Serial/Parent/Child titles before creating
- **Pricing Import:** Only adds pricing to parts that don't already have it
- **Oscar Import:** Checks for existing products by UPC before creating

## Requirements

### Python Environment
```bash
# Activate your virtual environment
C:\pythonstuff\parts_store\env\Scripts\activate

# Required packages (should already be installed)
pip install django
pip install django-oscar
pip install beautifulsoup4
pip install djangorestframework
pip install python-decouple
```

### Data Structure
- **Parts data:** HTML files in directory structure (Serial/Parent/Child folders)
- **Pricing data:** JSON files with pricing information
- **Database:** PostgreSQL with existing motorpartsdata models

## File Locations

All scripts should be placed in: `C:\pythonstuff\parts_store\epcstore\epcdata\`

```
epcstore/epcdata/
├── import_oscar_complete.ps1     # Main PowerShell script
├── import_oscar_simple.bat       # Simple batch script  
├── import_to_oscar.py            # Standalone Python script
├── scrapeandpush.py              # Parts import script
├── loadprices.py                 # Pricing import script
└── motorpartsdata/
    └── management/commands/
        └── import_to_oscar.py    # Django management command
```

## Logging

All scripts create log files:
- `oscar_import.log` - Main import process
- `scraper.log` - Parts import
- `pricing_loader.log` - Pricing import

## Error Handling

- **Validation:** All scripts validate input folders exist
- **Transactions:** Database operations wrapped in transactions
- **Rollback:** Failed imports are rolled back automatically
- **Detailed Logging:** All errors logged with context
- **Exit Codes:** Non-zero exit codes on failure for automation

## Testing

### Dry Run Mode
Test your import without making changes:
```powershell
.\import_oscar_complete.ps1 "C:\data\parts" "C:\data\pricing" -DryRun
```

### Single Serial Import
Test with one serial number first:
```powershell
.\import_oscar_complete.ps1 "C:\data\parts" "C:\data\pricing" -Serial "LSH14C4C5NA129710"
```

## Troubleshooting

### Common Issues:

1. **Virtual Environment Not Found**
   - Check path: `C:\pythonstuff\parts_store\env\Scripts\Activate.ps1`
   - Recreate if necessary

2. **Database Connection Issues**
   - Verify `.env` file exists with correct database credentials
   - Test database connection: `python manage.py dbshell`

3. **Missing Dependencies**
   - Install Oscar: `pip install django-oscar`
   - Run migrations: `python manage.py migrate`

4. **Permission Issues**
   - Run PowerShell as Administrator
   - Check file permissions on data folders

5. **Data Format Issues**
   - Verify HTML files have correct structure
   - Check JSON files are valid format
   - Review log files for specific errors

### Debug Mode:
Enable verbose logging for detailed output:
```powershell
.\import_oscar_complete.ps1 "C:\data\parts" "C:\data\pricing" -Verbose
```

## Support

Review the log files for detailed error information:
- Check `oscar_import.log` for main process errors
- Check `scraper.log` for parts import issues  
- Check `pricing_loader.log` for pricing import problems

The scripts include comprehensive error handling and will report specific issues encountered during the import process.

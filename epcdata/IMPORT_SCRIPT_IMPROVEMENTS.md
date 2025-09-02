# Import Script Improvements - Enhanced Error Handling

## Overview
The `import_to_oscar.py` management command has been updated with strict error handling and validation for pricing and stock data. **No more default values of 10 for missing data** - all errors are now properly logged and 0 values are used instead.

## Key Changes Made

### 1. Stock Handling (`_get_stock_info`)
**Before:** Used default stock of 10 when data was missing or invalid  
**After:** Strict validation with 0 stock for any errors

#### New Behavior:
- ❌ **No pricing data found** → Log error, return 0 stock
- ❌ **Missing stock_available field** → Log error, return 0 stock  
- ❌ **Invalid stock format** (non-numeric) → Log error, return 0 stock
- ❌ **Negative stock values** → Log warning, return 0 stock
- ✅ **Valid stock data** → Use actual value with proper parsing

#### Stock Format Support:
- `"0"` or `"nil"` → 0 stock
- `"10+"` → Extract numeric value (10)
- `"15"` → Parse as integer (15)
- `"1,500"` → Remove commas and parse (1500)

### 2. Price Handling (`_get_price_from_pricing_data`)
**Before:** Simple float conversion with basic error handling  
**After:** Comprehensive validation with detailed error logging

#### New Behavior:
- ❌ **No pricing data found** → Log error, return £0.00
- ❌ **Missing list_price field** → Log error, return £0.00
- ❌ **Invalid price format** → Log error, return £0.00
- ❌ **Negative prices** → Log warning, return £0.00
- ❌ **Unreasonably high prices** (>£99,999.99) → Log warning, return £0.00
- ✅ **Valid price data** → Clean formatting and round to 2 decimal places

#### Price Format Support:
- Removes currency symbols: `£`, `$`
- Removes commas: `1,234.56` → `1234.56`
- Validates numeric format
- Rounds to 2 decimal places

### 3. Enhanced Error Tracking

#### New Statistics Categories:
```python
{
    'categories_created': 0,
    'categories_existing': 0, 
    'products_created': 0,
    'products_existing': 0,
    'stock_created': 0,
    'stock_unchanged': 0,
    'errors': 0,               # Total errors
    'pricing_errors': 0,       # Price-related errors
    'stock_errors': 0,         # Stock-related errors  
    'validation_errors': 0     # Data validation errors
}
```

#### Enhanced Reporting:
- **Detailed error breakdown** by category
- **Data quality metrics** (error rate percentage)
- **Color-coded console output** (✅ success, ❌ errors, ⚠️ warnings)
- **Comprehensive file logging** with timestamps

### 4. Improved Console Output

#### Before:
```
Found stock data for C00112285: 10
No stock data found for C00112286, using default
```

#### After:
```
✅ Valid stock data for C00112285: 15
❌ No stock_available field or empty value for C00112286
⚠️ Negative stock value -5 for C00112287, setting to 0
```

## Usage Examples

### Run with verbose error tracking:
```bash
python manage.py import_to_oscar --verbose
```

### Import specific serial with detailed logging:
```bash
python manage.py import_to_oscar --serial "VM1234" --verbose
```

### Dry run to check data quality:
```bash
python manage.py import_to_oscar --dry-run --verbose
```

## Expected Results

### Improved Data Integrity:
- **0 stock** for products with missing/invalid stock data (instead of 10)
- **£0.00 price** for products with missing/invalid pricing data
- **Detailed error logs** for troubleshooting data quality issues

### Better Monitoring:
- **Error rate percentage** to track data quality over time
- **Categorized error tracking** to identify common issues
- **Timestamped log files** for audit trails

### Business Benefits:
- **No false inventory** (products show 0 stock instead of 10 when data is missing)
- **Accurate pricing** (products show £0.00 instead of invalid prices)
- **Better visibility** into data quality issues for corrective action

## Error Categories Explained

| Error Type | Description | Impact | Resolution |
|------------|-------------|---------|------------|
| **Pricing Errors** | Missing or invalid list_price data | Product shows £0.00 | Fix pricing data in source |
| **Stock Errors** | Missing or invalid stock_available data | Product shows 0 stock | Fix stock data in source |
| **Validation Errors** | Negative values or format issues | Corrected to safe defaults | Review data validation rules |

## Log File Output Example

```
2025-09-01 10:30:15 - ERROR - No pricing data found for part C00112285
2025-09-01 10:30:16 - ERROR - Invalid stock format 'abc' for part C00112286  
2025-09-01 10:30:17 - WARNING - Negative price -10.50 for part C00112287, setting to 0.00
2025-09-01 10:30:18 - INFO - ✅ Valid price data for C00112288: £25.99
```

This ensures **complete data integrity** and **transparent error reporting** for better inventory management.

# Maxus Product Removal Script

## Overview
The `remove_maxus_products.py` management command completely removes all Maxus products and their associated data from both the Oscar e-commerce models and the motorpartsdata models. This prepares the database for fresh product imports.

## ⚠️ CRITICAL WARNING
**This script permanently deletes data!** Once executed, all Maxus products, categories, stock records, and associated data will be permanently removed from the database.

## What Gets Removed

### Oscar E-commerce Data:
- **Categories**: All categories with "maxus" in name or slug
- **Products**: All products linked to Maxus categories  
- **Stock Records**: All stock/inventory data for Maxus products

### Motorpartsdata Source Data:
- **Serial Numbers**: All serials starting with "VM" (Maxus prefix)
- **Parent Titles**: All parent categories under VM serials
- **Child Titles**: All child categories under Maxus parents
- **Parts**: All individual parts under Maxus categories
- **Pricing Data**: All pricing information for Maxus parts

## Usage Examples

### 1. Safe Preview (Recommended First Step)
```bash
# See what would be deleted without actually deleting anything
python manage.py remove_maxus_products --dry-run --verbose
```

### 2. Detailed Preview
```bash
# Get comprehensive removal summary
python manage.py remove_maxus_products --dry-run
```

### 3. Interactive Deletion (Safest)
```bash
# Prompts for confirmation before deleting
python manage.py remove_maxus_products --verbose
```

### 4. Automated Deletion (Use with Caution)
```bash
# Skips confirmation prompt - dangerous!
python manage.py remove_maxus_products --confirm --verbose
```

## Command Options

| Option | Description | Safety Level |
|--------|-------------|--------------|
| `--dry-run` | Preview only, no deletion | ✅ SAFE |
| `--verbose` | Show detailed progress | ✅ SAFE |
| `--confirm` | Skip confirmation prompt | ⚠️ DANGEROUS |

## Safety Features

### 1. Confirmation Requirement
Without `--confirm` flag, the script requires typing `DELETE MAXUS` to proceed:
```
⚠️ WARNING: This will permanently delete ALL Maxus data!
Are you sure you want to continue? Type 'DELETE MAXUS' to confirm: 
```

### 2. Dry Run Mode
Always test with `--dry-run` first to see exactly what will be removed:
```bash
python manage.py remove_maxus_products --dry-run --verbose
```

### 3. Transaction Safety
All deletions happen within a database transaction - if any step fails, all changes are rolled back.

### 4. Detailed Logging
Creates timestamped log files: `maxus_removal_YYYYMMDD_HHMMSS.log`

## Expected Output

### Dry Run Example:
```
============================================================
🗑️  MAXUS PRODUCT REMOVAL SCRIPT
============================================================
🗄️ Database config: vansdirect as postgres on localhost
============================================================
📊 REMOVAL SUMMARY:
   Maxus Categories: 15
   Maxus Products: 1,234
   Stock Records: 1,234
   Serial Numbers (VM*): 45
   Parent Titles: 123
   Child Titles: 456
   Parts: 2,345
   Pricing Data: 2,345
============================================================
🔍 DRY RUN MODE - No data will be deleted
🗑️  Removing 2,345 pricing data records...
🗑️  Removing 1,234 stock records...
🗑️  Removing 1,234 products...
🗑️  Removing 2,345 parts...
🗑️  Removing 456 child titles...
🗑️  Removing 123 parent titles...
🗑️  Removing 45 serial numbers...
🗑️  Removing 15 categories...

=== Removal Statistics (DRY RUN) ===
Categories removed: 15
Products removed: 1,234
Stock records removed: 1,234
Parts removed: 2,345
Child titles removed: 456
Parent titles removed: 123
Serial numbers removed: 45
Pricing data removed: 2,345
Errors encountered: 0

🔍 Would remove 7,997 total records

🗄️ FINAL DATABASE VERIFICATION:
   Operations performed on database: vansdirect
   Remaining Maxus categories: 15
   Remaining VM serial numbers: 45
```

### Actual Deletion Example:
```
============================================================
🗑️  MAXUS PRODUCT REMOVAL SCRIPT
============================================================
⚠️ WARNING: This will permanently delete ALL Maxus data!
Are you sure you want to continue? Type 'DELETE MAXUS' to confirm: DELETE MAXUS
🗑️  DELETION MODE - Data will be permanently removed

=== Removal Statistics (ACTUAL DELETION) ===
Categories removed: 15
Products removed: 1,234
Stock records removed: 1,234
Parts removed: 2,345
Child titles removed: 456
Parent titles removed: 123
Serial numbers removed: 45
Pricing data removed: 2,345
Errors encountered: 0

✅ Successfully removed 7,997 total records

🗄️ FINAL DATABASE VERIFICATION:
   Operations performed on database: vansdirect
   Remaining Maxus categories: 0
   Remaining VM serial numbers: 0
✅ All Maxus data successfully removed

📝 Full log saved to: maxus_removal_20250901_143022.log
```

## Deletion Order (Foreign Key Safe)

The script removes data in the correct order to avoid foreign key constraint violations:

1. **Pricing Data** (references Parts)
2. **Stock Records** (references Products)  
3. **Products** (references Categories)
4. **Parts** (references Child Titles)
5. **Child Titles** (references Parent Titles)
6. **Parent Titles** (references Serial Numbers)
7. **Serial Numbers** (root motorpartsdata)
8. **Categories** (root Oscar data)

## After Removal

Once the script completes successfully:

1. **All Maxus data is permanently removed**
2. **Database is clean for fresh imports**
3. **Import script can be run without duplicates**
4. **Other vehicle brands (Peugeot, Renault, etc.) remain untouched**

## Troubleshooting

### Common Issues:

**Permission Errors:**
```bash
# Ensure proper database permissions
python manage.py check --database default
```

**Foreign Key Constraints:**
```bash
# Script handles this automatically, but if issues persist:
python manage.py remove_maxus_products --dry-run --verbose
```

**Partial Deletion:**
```bash
# Check remaining data:
python manage.py dbshell
SELECT COUNT(*) FROM catalogue_category WHERE name ILIKE '%maxus%';
SELECT COUNT(*) FROM motorpartsdata_serialnumber WHERE serial LIKE 'VM%';
```

## Recovery

**⚠️ There is no undo for this script!**

To recover deleted data:
1. Restore from database backup
2. Re-import from original data sources
3. Use version control to revert database migrations

## Best Practices

### Before Running:
1. **Create database backup**
2. **Run dry-run first**  
3. **Check removal summary carefully**
4. **Verify you're on correct database**

### During Execution:
1. **Use verbose mode for monitoring**
2. **Watch for error messages**
3. **Don't interrupt the process**

### After Completion:
1. **Verify database state**
2. **Check log files**
3. **Ready for fresh import**

## Integration with Import Script

After successful removal, you can run the import script fresh:

```bash
# Remove all Maxus data
python manage.py remove_maxus_products --verbose

# Import fresh Maxus data  
python manage.py import_to_oscar --verbose
```

This ensures no duplicate data and clean product hierarchy.

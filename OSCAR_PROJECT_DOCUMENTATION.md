# Oscar E-Commerce Project Documentation

## Project Overview

This project is designed to import Electronic Parts Catalog (EPC) data from HTML files into a Django-based Oscar e-commerce system. The data represents automotive parts with hierarchical organization and SVG diagrams.

---

## Database Models Architecture

### Model Hierarchy

```
SerialNumber (Vehicle/Model Identifier)
    ↓
ParentTitle (Main Category - e.g., "Air Intake System")
    ↓
ChildTitle (Sub-Category with SVG Diagram - e.g., "Air Filter")
    ↓
Part (Individual Part with Details)
    ↓
PricingData (Price, Stock, and Business Logic)
```

---

## Model Definitions

### 1. SerialNumber Model
**Purpose**: Represents a unique vehicle serial/VIN number and brand

**Fields**:
- `serial` (CharField, max 100, unique) - Vehicle serial/VIN number
- `vehicle_brand` (CharField, max 100, default='Maxus') - Brand name (Maxus, Peugeot, Renault, etc.)

**Relationships**: One-to-Many with ParentTitle

**Example**:
```
Serial: LSFAL11A4PA157987
Brand: Maxus
```

---

### 2. ParentTitle Model
**Purpose**: Represents main category groupings (top-level folders in HTML structure)

**Fields**:
- `title` (CharField, max 200) - Category name
- `serial_number` (ForeignKey → SerialNumber) - Links to specific vehicle

**Relationships**: 
- Many-to-One with SerialNumber
- One-to-Many with ChildTitle

**Example**:
```
Title: "Air Intake System"
Serial Number: LSFAL11A4PA157987
```

---

### 3. ChildTitle Model
**Purpose**: Represents specific diagrams/assemblies within a parent category

**Fields**:
- `title` (CharField, max 200) - Assembly/diagram name
- `parent` (ForeignKey → ParentTitle) - Links to parent category
- `svg_code` (TextField) - Complete SVG markup for the diagram

**Relationships**:
- Many-to-One with ParentTitle
- One-to-Many with Part

**Example**:
```
Title: "Air Filter"
Parent: Air Intake System
SVG Code: <svg xmlns="http://www.w3.org/2000/svg">...</svg>
```

**Important**: The SVG contains the visual diagram showing part locations with callout numbers

---

### 4. Part Model
**Purpose**: Individual part/component within an assembly

**Fields**:
- `child_title` (ForeignKey → ChildTitle) - Links to specific assembly
- `call_out_order` (IntegerField) - Position number in diagram
- `part_number` (CharField, max 100) - Manufacturer part number (SKU)
- `usage_name` (CharField, max 200) - Human-readable part description
- `unit_qty` (CharField, max 100) - Quantity needed in assembly
- `lr` (CharField, max 10, nullable) - Left/Right orientation
- `remark` (TextField, nullable) - Additional notes/conditions
- `nn_note` (TextField, nullable) - Internal notes
- `oscar_imported` (BooleanField, default=False) - Import tracking flag
- `oscar_imported_at` (DateTimeField, nullable) - Import timestamp

**Relationships**:
- Many-to-One with ChildTitle
- One-to-Many with PricingData

**Example**:
```
Part Number: 52365-T7001-00
Usage Name: "Air Filter Element"
Call Out Order: 1
Unit Qty: "1"
LR: "N/A"
Remark: "Standard filter"
Oscar Imported: False
```

---

### 5. PricingData Model
**Purpose**: Stores pricing, stock, and business logic for parts

**Fields**:
- `part_number` (ForeignKey → Part) - Links to specific part
- `replacement` (CharField, max 100, nullable) - Replacement part number
- `description` (CharField, max 100, nullable) - Additional description
- `active` (CharField, max 100, nullable) - Active status flag
- `oldest` (CharField, max 100, nullable) - Age/supersession info
- `range_code` (CharField, max 100, nullable) - Product range identifier
- `discount_code` (CharField, max 100, nullable) - Applicable discount
- `class_code` (CharField, max 100, nullable) - Part classification
- `vat_code` (CharField, max 100, nullable) - VAT/tax code
- `list_price` (CharField, max 100, nullable) - Retail price
- `vor` (CharField, max 100, nullable) - VOR (Vehicle Off Road) priority
- `stock_order` (CharField, max 100, nullable) - Stock ordering info
- `replacement_code` (CharField, max 100, nullable) - Replacement logic
- `whs` (CharField, max 100, nullable) - Warehouse location
- `stock_available` (CharField, max 100, nullable) - Current stock level
- `price_updated` (BooleanField, default=False) - Update tracking flag

**Relationships**: Many-to-One with Part

**Note**: Currently NOT populated by scrapeandpush.py - pricing imported separately (likely from Excel)

---

### 6. ShippingAddress Model
**Purpose**: Manages customer shipping addresses with country support

**Fields**:
- `name` (CharField, max 255)
- `address_line_1` (CharField, max 255)
- `address_line_2` (CharField, max 255, nullable)
- `city` (CharField, max 100)
- `state_province` (CharField, max 100, nullable)
- `postal_code` (CharField, max 20)
- `country` (CountryField) - Django Countries dropdown
- `phone` (CharField, max 20, nullable)
- `email` (EmailField, nullable)
- `is_default` (BooleanField, default=False)
- `created_at` (DateTimeField, auto_now_add)
- `updated_at` (DateTimeField, auto_now)

**Status**: Not related to parts import - used for Oscar checkout

---

### 7. ShippingMethod Model
**Purpose**: Defines available shipping options by country

**Fields**:
- `name` (CharField, max 100)
- `description` (TextField, nullable)
- `countries` (CountryField, multiple) - Multiple countries supported
- `price` (DecimalField, max_digits=10, decimal_places=2)
- `estimated_days_min` (IntegerField)
- `estimated_days_max` (IntegerField)
- `is_active` (BooleanField, default=True)
- `created_at` (DateTimeField, auto_now_add)

**Methods**:
- `delivery_estimate()` - Returns formatted delivery time string

**Status**: Not related to parts import - used for Oscar checkout

---

### 8. PriceUpdateTracker Model
**Purpose**: Audit log for price updates from Excel imports

**Fields**:
- `product_sku` (CharField, max 100, indexed) - Product SKU/UPC
- `price_updated` (BooleanField, default=True) - Update flag
- `old_price` (DecimalField, max_digits=12, decimal_places=2, nullable)
- `new_price` (DecimalField, max_digits=12, decimal_places=2)
- `update_date` (DateTimeField, default=timezone.now)
- `excel_filename` (CharField, max 255) - Source file
- `notes` (TextField, blank=True)
- `updated_by` (CharField, max 100, blank=True) - User identifier

**Class Methods**:
- `track_price_update()` - Helper to create tracking record
- `get_updated_products()` - Query updated products
- `reset_all_flags()` - Reset all update flags

**Indexes**: On `product_sku`, `update_date`, `price_updated`

**Status**: Used for price import auditing - separate from HTML scraping

---

## Data Import Script: scrapeandpush.py

### Purpose
Parses HTML files containing EPC diagrams and imports the structured data into Django models.

### How It Works

#### 1. Directory Structure Processing
```
LSFAL11A4PA157987/                    ← SerialNumber
  ├── air intake system/              ← ParentTitle
  │   └── Air filter.html             ← ChildTitle (contains SVG + Parts)
  ├── brakes/                         ← ParentTitle
  │   ├── Front Brakes.html           ← ChildTitle
  │   └── Rear Brakes.html            ← ChildTitle
  └── ...
```

#### 2. Script Flow

**Step 1: Create SerialNumber**
- Extracts serial from root directory name (e.g., "LSFAL11A4PA157987")
- Determines vehicle brand using `vehicle_utils.determine_vehicle_brand()`
- Creates or retrieves SerialNumber record

**Step 2: Create ParentTitle**
- For each subdirectory containing HTML files
- Uses directory name as title (e.g., "air intake system" → "Air Intake System")
- Creates or retrieves ParentTitle linked to SerialNumber

**Step 3: Parse HTML Files**
- Opens each HTML file in a directory
- Uses BeautifulSoup to parse content

**Step 4: Extract ChildTitle Data**
- Finds `<span id="legend-title">` for title
- Extracts entire `<svg>` element as string
- Creates ChildTitle record

**Step 5: Extract Parts Data**

**Parts Table (Left Side)**:
- Finds `<div class="parts-item">` with `data-callout` attribute
- Extracts:
  - Call out order (ordernumber)
  - Part number (from `<a class="text-link">`)
  - Description (from describe column)
  - Quantity (from quantity column)

**Extra Info (Right Side)**:
- Finds `<div class="parts-table-tbody-dflz">`
- Extracts:
  - Orientation (L/R/N/A)
  - Remarks/notes

**Step 6: Create Part Records**
- Combines left and right data by index
- Skips items where key fields are "N/A"
- Creates Part record linked to ChildTitle

### Key Features

**Duplicate Prevention**:
- Checks for existing SerialNumber before creating
- Checks for existing ParentTitle before creating
- **MISSING**: Does NOT check for existing ChildTitle (runs twice = duplicates)

**Error Handling**:
- Try-except blocks around parsing logic
- Logs all operations to both file and console
- Continues processing on individual item failures

**Logging**:
- Creates `scraper.log` file
- Logs INFO level: successful operations
- Logs ERROR level: validation failures, parsing errors
- Logs WARNING level: missing optional data

### Missing Functionality

1. **No Oscar Product Creation**: Script only populates custom models, doesn't create actual Oscar Product records
2. **No Pricing Import**: PricingData model not populated
3. **No ChildTitle Duplicate Check**: Re-running creates duplicate diagrams
4. **No Part Duplicate Check**: Re-running creates duplicate parts
5. **No vehicle_utils.py**: Imported but file not included in workspace

### Usage

```bash
python scrapeandpush.py /path/to/LSFAL11A4PA157987
```

---

## Current Status & Gaps

### ✅ What Works
- HTML parsing and data extraction
- Custom model population (SerialNumber, ParentTitle, ChildTitle, Part)
- Hierarchical structure preservation
- SVG diagram storage

### ❌ What's Missing
1. **Oscar Integration**: No actual Oscar Product/ProductClass/ProductAttribute creation
2. **Pricing Import**: Separate process, not documented
3. **Image Handling**: SVGs stored as text, not as images
4. **Stock Management**: No connection to inventory system
5. **Part Matching**: No logic to link same part across multiple diagrams

### 🔄 Recommended Next Steps (For Oscar Project)

1. **Create Oscar Import Script**:
   - Read from Part model
   - Create Oscar Product records
   - Map Part → Oscar Product
   - Update `oscar_imported` flags

2. **Add Duplicate Detection**:
   - Check existing ChildTitle before creating
   - Check existing Part before creating
   - Add unique constraints

3. **Create Pricing Import Script**:
   - Read Excel pricing files
   - Match by part_number
   - Populate PricingData model
   - Update Oscar product prices

4. **Add vehicle_utils.py**:
   - Document or create missing utility
   - Brand detection logic

---

## Data Statistics (Based on LSFAL11A4PA157987)

- **1 Serial Number**: LSFAL11A4PA157987 (Maxus)
- **~40+ Parent Categories**: body, brakes, charging, chassis, etc.
- **~150+ HTML Files**: Each represents a ChildTitle with diagram
- **Estimated 5,000-10,000+ Parts**: Across all diagrams

---

## File Locations

- **Models**: `epc_parts_store/epcdata/motorpartsdata/models.py`
- **Import Script**: `epc_parts_store/epcdata/scrapeandpush.py`
- **Serializers**: `epc_parts_store/epcdata/motorpartsdata/serializers.py` (referenced but not shown)
- **Sample Data**: `epc_parts_store/epcdata/LSFAL11A4PA157987/`

---

## Notes for Future Reference

1. **Django Settings**: Uses `epcdata.settings` module
2. **Database**: Likely PostgreSQL (Oscar recommendation) or MySQL
3. **Django Version**: Not specified - check requirements.txt
4. **Oscar Version**: Not specified - check requirements.txt
5. **Dependencies**: django-oscar, django-countries, beautifulsoup4

---

## Migration Considerations

When moving away from Oscar to WooCommerce, this structure provides:
- Clear data hierarchy (SerialNumber → Parent → Child → Part)
- Complete SVG diagrams stored as text
- Part relationships and metadata
- Clean separation of concerns

The data can be exported and transformed for WooCommerce without losing information.

# Stock Handling Update - "10+" to 11 Conversion

## Change Summary
Updated the `import_to_oscar.py` script to handle "+" stock indicators properly by adding 1 to the base value.

## Updated Logic

### Before:
```python
elif stock_str.endswith('+'):
    # Extract number from "10+" format
    stock = int(stock_str.replace('+', ''))  # "10+" became 10
```

### After:
```python
elif stock_str.endswith('+'):
    # Extract number from "10+" format and add 1 for "+" indicator
    base_stock = int(stock_str.replace('+', ''))
    stock = base_stock + 1  # "10+" becomes 11, "5+" becomes 6, etc.
    if self.verbose:
        self.stdout.write(f"📦 Stock '{stock_str}' converted to {stock} for {part.part_number}")
```

## Stock Value Conversions

| Original Value | Previous Result | New Result |
|----------------|-----------------|------------|
| `"10+"`       | 10              | **11**     |
| `"5+"`        | 5               | **6**      |
| `"25+"`       | 25              | **26**     |
| `"1+"`        | 1               | **2**      |
| `"0+"`        | 0               | **1**      |

## Rationale

The "+" symbol in stock availability typically indicates "or more" - meaning there are **at least** that many items in stock, possibly more. By adding 1 to the base value:

1. **Better represents availability** - "10+" means at least 10, so 11 is a reasonable estimate
2. **Distinguishes from exact counts** - "10" vs "10+" now show as 10 vs 11 
3. **Conservative but optimistic** - Shows slightly more stock than minimum without being unrealistic

## Files Updated

- ✅ `epcdata/management/commands/import_to_oscar.py` - Updated stock processing logic
- ℹ️ `loadprices.py` - No changes needed (only stores raw values from JSON)

## Expected Console Output

When running with `--verbose`, you'll now see:
```
📦 Stock '10+' converted to 11 for C00112285
📦 Stock '5+' converted to 6 for C00112286
✅ Valid stock data for C00112285: 11
```

## Testing

After dropping and recreating the database with fresh imports:
1. Products with "10+" stock will show 11 in stock
2. Products with exact stock numbers remain unchanged
3. All other stock handling logic remains the same (0 for errors, etc.)

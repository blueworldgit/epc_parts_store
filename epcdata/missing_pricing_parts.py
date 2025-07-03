from motorpartsdata.models import SerialNumber, Part, PricingData

serial_input = "LSH14J7CXMA114599"  # Replace with your serial number

try:
    serial = SerialNumber.objects.get(serial=serial_input)
except SerialNumber.DoesNotExist:
    print(f"Serial number '{serial_input}' not found.")
    missing_pricing_parts = []
else:
    # Get all parts for this serial number through the relationship chain
    parts = Part.objects.filter(child_title__parent__serial_number=serial)
    
    missing_pricing_parts = []
    seen_part_numbers = set()
    
    for part in parts:
        # Skip if we've already processed this part number
        if part.part_number in seen_part_numbers:
            continue
        seen_part_numbers.add(part.part_number)
        
        # Check if this specific part instance has pricing data
        if not PricingData.objects.filter(part_number=part).exists():
            missing_pricing_parts.append(part.part_number)
    
    # Sort the results
    missing_pricing_parts = sorted(missing_pricing_parts)

# Save to next.txt
with open("next.txt", "w", encoding="utf-8") as f:
    f.write(str(missing_pricing_parts))

print(f"Found {len(missing_pricing_parts)} part numbers without pricing data for serial {serial_input}")
print(f"Total results: {len(missing_pricing_parts)}")
print("Missing pricing parts:", missing_pricing_parts)
print("Results saved to next.txt")

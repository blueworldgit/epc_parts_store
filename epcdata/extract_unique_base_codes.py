#!/usr/bin/env python3
"""
Extract unique base part codes from stockreport.txt (without color/variant suffixes)
"""
import re
import os

def extract_unique_base_codes():
    """Extract unique base part numbers from stockreport.txt"""
    
    # Read the stockreport file
    report_file = "stockreport.txt"
    if not os.path.exists(report_file):
        print(f"❌ File {report_file} not found!")
        return []
    
    base_codes = set()  # Use set to automatically handle duplicates
    
    with open(report_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"📄 Reading {report_file}...")
    
    # Skip header lines (first 2 lines)
    data_lines = lines[2:]
    
    for line_num, line in enumerate(data_lines, start=3):
        line = line.strip()
        
        # Skip empty lines
        if not line:
            continue
            
        # Extract part number (first column, up to first space)
        # Part numbers can have format like: C00123456, B00004107, C00000601-A133, C00073043-bla
        match = re.match(r'^([BC]\d{8})(?:-[A-Z0-9]+)?', line)
        
        if match:
            base_code = match.group(1)  # Only the base code without suffix
            base_codes.add(base_code)
            
            # Only print first few for verification
            if len(base_codes) <= 10:
                print(f"  ✅ Line {line_num:3d}: {match.group(0)} -> {base_code}")
    
    # Convert to sorted list
    codes_list = sorted(list(base_codes))
    
    print(f"\n📊 EXTRACTION SUMMARY:")
    print(f"   Total unique base codes: {len(codes_list)}")
    print(f"   First 10 codes: {codes_list[:10]}")
    print(f"   Last 10 codes: {codes_list[-10:]}")
    
    return codes_list

def save_codes_array(codes):
    """Save codes as Python array format"""
    if not codes:
        print("❌ No codes to save!")
        return
    
    filename = "unique_base_codes_array.py"
    
    # Create array with 10 codes per line for readability
    array_lines = []
    for i in range(0, len(codes), 10):
        chunk = codes[i:i+10]
        formatted_chunk = ', '.join(f'"{code}"' for code in chunk)
        array_lines.append(f"    {formatted_chunk},")
    
    # Remove trailing comma from last line
    if array_lines:
        array_lines[-1] = array_lines[-1].rstrip(',')
    
    content = f'''#!/usr/bin/env python3
"""
Unique base part codes extracted from stockreport.txt
Generated automatically - {len(codes)} codes
"""

codes = [
{chr(10).join(array_lines)}
]

print(f"Array contains {{len(codes)}} unique base part codes")
'''
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Saved {len(codes)} codes to {filename}")

if __name__ == "__main__":
    print("🔍 Extracting unique base part codes from stockreport.txt...")
    codes = extract_unique_base_codes()
    
    if codes:
        save_codes_array(codes)
        print(f"\n🎉 Successfully extracted {len(codes)} unique base codes!")
    else:
        print("\n❌ No codes extracted!")
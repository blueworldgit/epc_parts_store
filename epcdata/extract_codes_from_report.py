#!/usr/bin/env python3
"""
Extract part codes from stockreport.txt and generate Python array
"""
import re
import os

def extract_codes_from_stockreport():
    """Extract part numbers from stockreport.txt"""
    
    # Read the stockreport file
    report_file = "stockreport.txt"
    if not os.path.exists(report_file):
        print(f"❌ File {report_file} not found!")
        return []
    
    codes = []
    
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
        # Part numbers can have format like: C00123456, B00004107, C00000601-A133
        match = re.match(r'^([BC]\d{8}(?:-[A-Z0-9]+)?)', line)
        
        if match:
            part_code = match.group(1)
            codes.append(part_code)
            print(f"  ✅ Line {line_num:3d}: {part_code}")
        else:
            print(f"  ⚠️  Line {line_num:3d}: Could not extract code from: {line[:50]}...")
    
    print(f"\n📊 EXTRACTION SUMMARY:")
    print(f"   Total codes extracted: {len(codes)}")
    print(f"   First 5 codes: {codes[:5]}")
    print(f"   Last 5 codes: {codes[-5:]}")
    
    return codes

def generate_python_array(codes):
    """Generate Python array format"""
    
    # Create the array string with proper formatting
    array_lines = ['codes = [']
    
    # Add codes in groups of 10 per line for readability
    for i in range(0, len(codes), 10):
        group = codes[i:i+10]
        line = '    ' + ', '.join(f'"{code}"' for code in group)
        
        # Add comma if not the last group
        if i + 10 < len(codes):
            line += ','
        
        array_lines.append(line)
    
    array_lines.append(']')
    
    return '\n'.join(array_lines)

def save_array_to_file(array_string, filename="extracted_codes_array.py"):
    """Save the array to a Python file"""
    
    header = f'''#!/usr/bin/env python3
"""
Auto-generated part codes array from stockreport.txt
Generated on: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Total codes: {array_string.count('"')//2}
"""

'''
    
    full_content = header + array_string
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(full_content)
    
    print(f"💾 Array saved to: {filename}")
    return filename

if __name__ == "__main__":
    print("🔍 EXTRACTING PART CODES FROM STOCKREPORT")
    print("=" * 50)
    
    # Extract codes
    codes = extract_codes_from_stockreport()
    
    if codes:
        # Generate array
        array_string = generate_python_array(codes)
        
        # Save to file
        array_file = save_array_to_file(array_string)
        
        # Show preview
        print(f"\n📝 ARRAY PREVIEW:")
        print("=" * 30)
        print(array_string[:500] + "..." if len(array_string) > 500 else array_string)
        
        print(f"\n✅ SUCCESS!")
        print(f"   Extracted {len(codes)} codes")
        print(f"   Array saved to: {array_file}")
        print(f"   You can now copy this array into your scraper!")
        
    else:
        print("❌ No codes extracted!")
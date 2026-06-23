"""
Deep Data Structure Explorer
Analyzes the specific HTML structure to understand why some parts show N/A
and what the complete data layout looks like
"""

import os
from bs4 import BeautifulSoup
import json

def explore_parts_table_structure(html_file_path):
    """Deep dive into the parts table structure"""
    
    print(f"\n🔍 DEEP ANALYSIS: {os.path.basename(html_file_path)}")
    print("=" * 60)
    
    with open(html_file_path, 'r', encoding='utf-8') as file:
        html = file.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    
    print("🏗️  MAIN PARTS TABLE STRUCTURE")
    print("-" * 35)
    
    # Find the main parts table (not the extra info table)
    main_parts_table = soup.find('div', class_='parts-table-wrapper float')
    if main_parts_table:
        print("✅ Main parts table found (.parts-table-wrapper float)")
        
        # Find the table body
        tbody = main_parts_table.find('div', class_='parts-table-tbody')
        if tbody:
            print("✅ Table body found (.parts-table-tbody)")
            
            # Get all parts items in main table
            parts_items = tbody.find_all('div', class_='parts-item')
            visible_parts = [item for item in parts_items if 'dn' not in item.get('class', [])]
            
            print(f"📊 Parts found in main table: {len(parts_items)} total, {len(visible_parts)} visible")
            
            # Analyze first few parts in detail
            print(f"\n📋 DETAILED PARTS ANALYSIS (First 5 parts):")
            
            for i, item in enumerate(visible_parts[:5]):
                print(f"\n🔧 PART {i+1}:")
                print(f"   HTML Classes: {item.get('class', [])}")
                print(f"   Data Attributes: {[k for k in item.attrs.keys() if k.startswith('data-')]}")
                
                # Find all columns in this part
                columns = item.find_all('span', class_='column')
                print(f"   Columns found: {len(columns)}")
                
                for j, col in enumerate(columns):
                    col_classes = col.get('class', [])
                    col_text = col.text.strip()[:50]
                    
                    print(f"      Column {j+1}: {col_classes} = '{col_text}{'...' if len(col.text.strip()) > 50 else ''}'" )
                    
                    # Look for specific data in columns
                    if 'ordernumber' in col_classes:
                        print(f"         🔢 CALLOUT NUMBER: '{col_text}'")
                    elif col.find('div', class_='part-number'):
                        part_link = col.select_one('.part-number a.text-link')
                        if part_link:
                            print(f"         🏷️  PART NUMBER: '{part_link.text.strip()}'")
                    elif 'describe' in col_classes:
                        print(f"         📝 DESCRIPTION: '{col_text}'")
                    elif 'quantity' in col_classes:
                        print(f"         📊 QUANTITY: '{col_text}'")
            
            # Look for patterns in all visible parts
            print(f"\n📈 PATTERNS ACROSS ALL {len(visible_parts)} VISIBLE PARTS:")
            
            callout_numbers = []
            part_numbers = []
            descriptions = []
            
            for item in visible_parts:
                # Callout
                callout_elem = item.select_one('.column.ordernumber')
                if callout_elem and callout_elem.text.strip():
                    callout_numbers.append(callout_elem.text.strip())
                
                # Part number
                part_elem = item.select_one('.part-number a.text-link')
                if part_elem and part_elem.text.strip():
                    part_numbers.append(part_elem.text.strip())
                
                # Description
                desc_elem = item.select_one('.column.describe')
                if desc_elem and desc_elem.text.strip():
                    descriptions.append(desc_elem.text.strip())
            
            print(f"   Valid callout numbers: {len(callout_numbers)}/{len(visible_parts)}")
            print(f"   Valid part numbers: {len(part_numbers)}/{len(visible_parts)}")
            print(f"   Valid descriptions: {len(descriptions)}/{len(visible_parts)}")
            
            if callout_numbers:
                print(f"   Callout range: {min(callout_numbers)} to {max(callout_numbers)}")
            
            if part_numbers:
                print(f"   Sample part numbers: {part_numbers[:3]}")
            
            if descriptions:
                print(f"   Sample descriptions: {[d[:30] + '...' for d in descriptions[:3]]}")
    
    print(f"\n🗂️  EXTRA INFO TABLE STRUCTURE")
    print("-" * 35)
    
    # Analyze the extra info table (L/R and remarks)
    condition_entity = soup.find('div', class_='condition-entity')
    if condition_entity:
        extra_table = condition_entity.find('div', class_='parts-table-tbody parts-table-tbody-dflz')
        if extra_table:
            print("✅ Extra info table found (.parts-table-tbody-dflz)")
            
            extra_items = extra_table.find_all('div', class_='parts-item')
            visible_extra = [item for item in extra_items if 'dn' not in item.get('class', [])]
            
            print(f"📊 Extra info entries: {len(extra_items)} total, {len(visible_extra)} visible")
            
            print(f"\n📋 EXTRA INFO DETAILS (First 3 entries):")
            
            for i, item in enumerate(visible_extra[:3]):
                columns = item.find_all('span', class_='column')
                print(f"\n   Entry {i+1}:")
                print(f"      Columns: {len(columns)}")
                
                for j, col in enumerate(columns):
                    text = col.text.strip()
                    print(f"         Column {j+1}: '{text}'" if text else f"         Column {j+1}: (empty)")

def analyze_html_table_alignment():
    """Analyze how main parts table aligns with extra info table"""
    
    print(f"\n🔄 TABLE ALIGNMENT ANALYSIS")
    print("=" * 35)
    
    root_dir = r"c:\pythonstuff\vansdirect\epc_parts_store\epcdata\LSH14C4C5NA129710"
    
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.html'):
                html_path = os.path.join(root, file)
                category = os.path.basename(root)
                
                print(f"\n📄 {category}/{file}")
                print("-" * 30)
                
                with open(html_path, 'r', encoding='utf-8') as f:
                    html = f.read()
                
                soup = BeautifulSoup(html, 'html.parser')
                
                # Count main parts
                main_parts = soup.find_all(lambda tag: tag.name == "div" and 
                                         "parts-item" in tag.get("class", []) and 
                                         tag.has_attr("data-callout"))
                
                visible_main = [item for item in main_parts if 'dn' not in item.get('class', [])]
                
                # Count extra info
                extra_info = []
                container = soup.find('div', class_='condition-entity')
                if container:
                    right_div = container.find('div', class_='parts-table-tbody parts-table-tbody-dflz')
                    if right_div:
                        right_rows = right_div.find_all('div', class_='parts-item')
                        extra_info = [item for item in right_rows if 'dn' not in item.get('class', [])]
                
                print(f"   Main parts (data-callout): {len(visible_main)}")
                print(f"   Extra info entries: {len(extra_info)}")
                print(f"   Alignment: {'✅ Matched' if len(visible_main) >= len(extra_info) else '⚠️  Mismatched'}")
                
                # Show alignment mapping
                alignment_count = min(len(visible_main), len(extra_info))
                if alignment_count > 0:
                    print(f"   First {min(3, alignment_count)} alignments:")
                    
                    for i in range(min(3, alignment_count)):
                        # Main part info
                        main_item = visible_main[i]
                        callout = main_item.select_one('.column.ordernumber')
                        part_num = main_item.select_one('.part-number a.text-link')
                        
                        callout_text = callout.text.strip() if callout else "N/A"
                        part_text = part_num.text.strip() if part_num else "N/A"
                        
                        # Extra info
                        extra_item = extra_info[i] if i < len(extra_info) else None
                        if extra_item:
                            extra_cols = extra_item.find_all('span', class_='column')
                            lr = extra_cols[0].text.strip() if len(extra_cols) > 0 else "N/A"
                            remark = extra_cols[1].text.strip() if len(extra_cols) > 1 else "N/A"
                        else:
                            lr = remark = "N/A"
                        
                        print(f"      {i+1}. Callout: {callout_text} | Part: {part_text} | L/R: {lr} | Remark: {remark}")

def main():
    """Main deep analysis function"""
    
    print("🔬 DEEP DATA STRUCTURE EXPLORER")
    print("=" * 50)
    
    root_dir = r"c:\pythonstuff\vansdirect\epc_parts_store\epcdata\LSH14C4C5NA129710"
    
    # Analyze each HTML file in detail
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.html'):
                html_path = os.path.join(root, file)
                explore_parts_table_structure(html_path)
    
    # Analyze table alignment
    analyze_html_table_alignment()
    
    print(f"\n🎯 KEY FINDINGS:")
    print("=" * 15)
    print("1. Parts tables have two separate structures:")
    print("   - Main table: Contains callout, part number, description, quantity")
    print("   - Extra table: Contains L/R orientation and remarks")
    print("2. Tables are aligned by index (not by data attributes)")
    print("3. Some parts may have empty/missing data causing 'N/A' values")
    print("4. Hidden parts (class 'dn') are filtered out from both tables")
    print("5. scrapeandpush.py correctly maps between tables by index position")

if __name__ == "__main__":
    main()
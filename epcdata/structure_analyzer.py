"""
Directory Structure Analysis Script
Analyzes the LSH14C4C5NA129710 folder structure and provides detailed insights
"""

import os
import json
from pathlib import Path
from bs4 import BeautifulSoup

def analyze_directory_structure(root_path):
    """Analyze the complete directory structure and file contents"""
    
    analysis = {
        "root_directory": os.path.basename(root_path),
        "total_directories": 0,
        "total_html_files": 0,
        "categories": {},
        "file_sizes": {},
        "html_structure_summary": {}
    }
    
    print(f"=== Directory Structure Analysis ===")
    print(f"Root Directory: {root_path}")
    print(f"Vehicle Serial: {os.path.basename(root_path)}")
    print()
    
    # Walk through directory structure
    for root, dirs, files in os.walk(root_path):
        relative_path = os.path.relpath(root, root_path)
        
        # Skip the root directory itself for directory counting
        if relative_path != '.':
            analysis["total_directories"] += 1
            category_name = os.path.basename(root)
            
            # Analyze files in this directory
            html_files = [f for f in files if f.endswith('.html')]
            other_files = [f for f in files if not f.endswith('.html')]
            
            analysis["categories"][category_name] = {
                "html_files": len(html_files),
                "other_files": len(other_files),
                "file_list": files
            }
            
            # File size analysis
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    size = os.path.getsize(file_path)
                    analysis["file_sizes"][f"{category_name}/{file}"] = size
                    if file.endswith('.html'):
                        analysis["total_html_files"] += 1
                except OSError:
                    analysis["file_sizes"][f"{category_name}/{file}"] = "Error reading"
            
            print(f"📁 Category: {category_name}")
            print(f"   HTML Files: {len(html_files)}")
            print(f"   Other Files: {len(other_files)}")
            print(f"   Files: {', '.join(files)}")
            print()
    
    # Special handling for root directory files
    if os.path.exists(root_path):
        root_files = [f for f in os.listdir(root_path) if os.path.isfile(os.path.join(root_path, f))]
        if root_files:
            analysis["root_files"] = root_files
            print(f"📄 Root Directory Files: {', '.join(root_files)}")
            for file in root_files:
                file_path = os.path.join(root_path, file)
                try:
                    analysis["file_sizes"][file] = os.path.getsize(file_path)
                except OSError:
                    analysis["file_sizes"][file] = "Error reading"
            print()
    
    return analysis

def analyze_html_content(html_file_path):
    """Analyze the content structure of an HTML file"""
    
    try:
        with open(html_file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        analysis = {
            "file_path": html_file_path,
            "file_size": len(html_content),
            "legend_title": None,
            "has_svg": False,
            "svg_dimensions": None,
            "total_parts": 0,
            "visible_parts": 0,
            "hidden_parts": 0,
            "callout_numbers": [],
            "part_numbers": [],
            "sample_parts": []
        }
        
        # Extract legend title
        legend_title = soup.find('span', id='legend-title')
        if legend_title:
            analysis["legend_title"] = legend_title.text.strip()
        
        # Check for SVG
        svg_element = soup.find('svg', attrs={"xmlns": "http://www.w3.org/2000/svg"})
        if svg_element:
            analysis["has_svg"] = True
            width = svg_element.get('width', 'Unknown')
            height = svg_element.get('height', 'Unknown') 
            analysis["svg_dimensions"] = f"{width} x {height}"
        
        # Analyze parts
        parts_items = soup.find_all('div', class_='parts-item')
        analysis["total_parts"] = len(parts_items)
        
        # Filter visible vs hidden parts
        visible_parts = [item for item in parts_items if 'dn' not in item.get('class', [])]
        hidden_parts = [item for item in parts_items if 'dn' in item.get('class', [])]
        
        analysis["visible_parts"] = len(visible_parts)
        analysis["hidden_parts"] = len(hidden_parts)
        
        # Extract sample data from first few visible parts
        for i, item in enumerate(visible_parts[:3]):  # First 3 parts as samples
            part_data = {}
            
            # Callout number
            callout_elem = item.find('span', class_='column ordernumber')
            if callout_elem:
                callout = callout_elem.text.strip()
                part_data["callout"] = callout
                analysis["callout_numbers"].append(callout)
            
            # Part number  
            part_num_elem = item.select_one('.part-number a.text-link')
            if part_num_elem:
                part_number = part_num_elem.text.strip()
                part_data["part_number"] = part_number
                analysis["part_numbers"].append(part_number)
            
            # Description
            desc_elem = item.find('span', class_='column describe')
            if desc_elem:
                part_data["description"] = desc_elem.text.strip()
            
            # Quantity
            qty_elem = item.find('span', class_='column quantity')
            if qty_elem:
                part_data["quantity"] = qty_elem.text.strip()
            
            analysis["sample_parts"].append(part_data)
        
        return analysis
        
    except Exception as e:
        return {"error": f"Failed to analyze {html_file_path}: {str(e)}"}

def main():
    """Main analysis function"""
    
    # Define the path to analyze
    root_path = r"c:\pythonstuff\vansdirect\epc_parts_store\epcdata\LSH14C4C5NA129710"
    
    print("🔍 VEHICLE PARTS DATA STRUCTURE ANALYSIS")
    print("=" * 50)
    
    # Overall directory analysis
    dir_analysis = analyze_directory_structure(root_path)
    
    print(f"📊 SUMMARY STATISTICS")
    print(f"Total Categories: {dir_analysis['total_directories']}")
    print(f"Total HTML Files: {dir_analysis['total_html_files']}")
    print()
    
    # Analyze each HTML file in detail
    print(f"🔬 DETAILED HTML FILE ANALYSIS")
    print("=" * 30)
    
    html_analyses = {}
    for category, info in dir_analysis['categories'].items():
        if info['html_files'] > 0:
            # Find HTML files in this category
            category_path = os.path.join(root_path, category)
            for file in os.listdir(category_path):
                if file.endswith('.html'):
                    html_file_path = os.path.join(category_path, file)
                    print(f"\n📄 Analyzing: {category}/{file}")
                    
                    html_analysis = analyze_html_content(html_file_path)
                    html_analyses[f"{category}/{file}"] = html_analysis
                    
                    if "error" not in html_analysis:
                        print(f"   Title: {html_analysis['legend_title']}")
                        print(f"   File Size: {html_analysis['file_size']:,} bytes")
                        print(f"   Has SVG: {html_analysis['has_svg']}")
                        if html_analysis['has_svg']:
                            print(f"   SVG Size: {html_analysis['svg_dimensions']}")
                        print(f"   Total Parts: {html_analysis['total_parts']}")
                        print(f"   Visible Parts: {html_analysis['visible_parts']}")
                        print(f"   Hidden Parts: {html_analysis['hidden_parts']}")
                        
                        if html_analysis['sample_parts']:
                            print(f"   Sample Parts:")
                            for part in html_analysis['sample_parts']:
                                print(f"     - Callout {part.get('callout', 'N/A')}: "
                                      f"{part.get('part_number', 'N/A')} - "
                                      f"{part.get('description', 'N/A')[:50]}...")
                    else:
                        print(f"   ❌ {html_analysis['error']}")
    
    # Save analysis to JSON file
    output_file = "structure_analysis.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "directory_analysis": dir_analysis,
            "html_file_analyses": html_analyses
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Analysis saved to: {output_file}")
    
    # Print final summary
    print(f"\n🎯 PROCESSING READINESS")
    print("=" * 25)
    total_visible_parts = sum(analysis.get('visible_parts', 0) 
                             for analysis in html_analyses.values() 
                             if 'error' not in analysis)
    print(f"Ready for processing: {dir_analysis['total_html_files']} files")
    print(f"Total extractable parts: {total_visible_parts}")
    print(f"Vehicle Serial: {dir_analysis['root_directory']}")

if __name__ == "__main__":
    main()
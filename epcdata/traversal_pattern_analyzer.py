"""
Traversal Pattern Analysis Script
Studies the scrapeandpush.py methodology to understand data traversal patterns
without requiring Django setup
"""

import os
from bs4 import BeautifulSoup
import json

class TraversalPatternAnalyzer:
    """Analyzes traversal patterns based on scrapeandpush.py methodology"""
    
    def __init__(self):
        self.analysis = {
            "traversal_methodology": {},
            "extraction_patterns": {},
            "data_hierarchy": {},
            "file_processing_stats": {}
        }
    
    def analyze_traversal_methodology(self, root_dir):
        """Study how scrapeandpush.py traverses directories"""
        
        print("🗂️  TRAVERSAL METHODOLOGY ANALYSIS")
        print("=" * 45)
        print(f"Analyzing directory: {root_dir}")
        print(f"Based on scrapeandpush.py patterns\n")
        
        # Step 1: Extract serial number from root directory (like scrapeandpush.py)
        serial_name = os.path.basename(root_dir)
        print(f"📋 STEP 1: Extract Serial Number")
        print(f"   Root directory name: {serial_name}")
        print(f"   Serial extracted: {serial_name}")
        
        # Step 2: Walk directory structure (os.walk pattern from scrapeandpush.py)
        print(f"\n📁 STEP 2: Directory Traversal (os.walk)")
        
        directory_structure = {}
        processing_order = []
        
        for dirpath, dirnames, filenames in os.walk(root_dir):
            relative_path = os.path.relpath(dirpath, root_dir)
            
            # Skip root directory (matches scrapeandpush.py logic)
            if relative_path == '.':
                root_files = [f for f in filenames if f.endswith('.txt')]
                if root_files:
                    print(f"   Root files found: {root_files}")
                continue
            
            # Find HTML files (scrapeandpush.py only processes dirs with HTML)
            html_files = [f for f in filenames if f.lower().endswith('.html')]
            
            if html_files:
                parent_name = os.path.basename(dirpath)
                formatted_parent = parent_name.replace('_', ' ').title()
                
                directory_structure[parent_name] = {
                    "original_name": parent_name,
                    "formatted_name": formatted_parent,
                    "html_files": html_files,
                    "file_count": len(html_files)
                }
                
                processing_order.append(parent_name)
                
                print(f"   📂 Category: '{parent_name}' -> '{formatted_parent}'")
                print(f"      HTML files: {html_files}")
        
        self.analysis["traversal_methodology"] = {
            "serial_number": serial_name,
            "directory_structure": directory_structure,
            "processing_order": processing_order,
            "categories_found": len(directory_structure)
        }
        
        return directory_structure
    
    def analyze_html_parsing_pattern(self, html_file_path, category_name):
        """Study how scrapeandpush.py parses HTML files"""
        
        print(f"\n🔍 HTML PARSING PATTERN: {category_name}")
        print("-" * 40)
        
        try:
            with open(html_file_path, 'r', encoding='utf-8') as file:
                html = file.read()
            
            soup = BeautifulSoup(html, 'html.parser')
            
            parsing_results = {
                "file_path": html_file_path,
                "category": category_name,
                "extraction_steps": {}
            }
            
            # Step 1: Extract legend title (scrapeandpush.py pattern)
            print("   📝 STEP 1: Legend Title Extraction")
            legend_title = soup.find('span', id='legend-title')
            if legend_title:
                title_content = legend_title.text.strip()
                parsing_results["extraction_steps"]["title"] = {
                    "found": True,
                    "content": title_content,
                    "method": "soup.find('span', id='legend-title')"
                }
                print(f"      ✅ Found: '{title_content}'")
            else:
                fallback_title = os.path.basename(html_file_path).replace('.html', '')
                parsing_results["extraction_steps"]["title"] = {
                    "found": False,
                    "content": fallback_title,
                    "method": "filename fallback"
                }
                print(f"      ⚠️  Using fallback: '{fallback_title}'")
            
            # Step 2: Extract SVG (scrapeandpush.py pattern)
            print("   🎨 STEP 2: SVG Extraction")
            svg_element = soup.find('svg', attrs={"xmlns": "http://www.w3.org/2000/svg"})
            if svg_element:
                svg_content = str(svg_element)
                parsing_results["extraction_steps"]["svg"] = {
                    "found": True,
                    "size": len(svg_content),
                    "method": "soup.find('svg', attrs={'xmlns': 'http://www.w3.org/2000/svg'})"
                }
                print(f"      ✅ SVG found: {len(svg_content):,} characters")
            else:
                parsing_results["extraction_steps"]["svg"] = {
                    "found": False,
                    "size": 0,
                    "method": "defaulted to <svg></svg>"
                }
                print(f"      ❌ No SVG found")
            
            # Step 3: Extract extra info (orientation & remarks - scrapeandpush.py pattern)
            print("   📊 STEP 3: Extra Info Extraction (L/R & Remarks)")
            extra = []
            try:
                container = soup.find('div', class_='condition-entity')
                if container:
                    right_div = container.find('div', class_='parts-table-tbody parts-table-tbody-dflz')
                    if right_div:
                        right_rows = right_div.find_all('div', class_='parts-item')
                        filtered_items = [item for item in right_rows if 'dn' not in item.get('class', [])]
                        
                        for item in filtered_items:
                            first_column = item.find(lambda tag: tag.name == "span" and tag.get("class") == ["column"])
                            orientation = first_column.text.strip() if first_column else "N/A"
                            
                            note_column = item.select_one('.text-column-note span')
                            remark = note_column.text.strip() if note_column else "N/A"
                            
                            extra.append({
                                'orientation': orientation,
                                'remark': remark
                            })
                
                parsing_results["extraction_steps"]["extra_info"] = {
                    "count": len(extra),
                    "method": "Complex DOM traversal for L/R and remarks",
                    "sample": extra[:2] if extra else []
                }
                print(f"      ✅ Extra info entries: {len(extra)}")
                
            except Exception as e:
                parsing_results["extraction_steps"]["extra_info"] = {
                    "count": 0,
                    "error": str(e),
                    "method": "Failed extraction"
                }
                print(f"      ❌ Extra info error: {str(e)}")
            
            # Step 4: Extract main parts data (scrapeandpush.py main logic)
            print("   🔧 STEP 4: Parts Data Extraction")
            
            # Find parts items with data-callout (exact scrapeandpush.py logic)
            parts_items = soup.find_all(lambda tag: tag.name == "div" and 
                                      "parts-item" in tag.get("class", []) and 
                                      tag.has_attr("data-callout"))
            
            # Filter out hidden items (dn class) - scrapeandpush.py pattern
            filtered_items = [item for item in parts_items if 'dn' not in item.get('class', [])]
            
            print(f"      📋 Total parts items with data-callout: {len(parts_items)}")
            print(f"      👁️  Visible parts items (no .dn class): {len(filtered_items)}")
            
            extracted_parts = []
            successful_extractions = 0
            
            for count, item in enumerate(filtered_items):
                try:
                    # Get extra info if available (scrapeandpush.py pattern)
                    orientation = extra[count]['orientation'] if count < len(extra) else "N/A"
                    notes = extra[count]['remark'] if count < len(extra) else "N/A"
                    
                    # Extract fields using exact scrapeandpush.py selectors
                    order_number_elem = item.select_one('.column.ordernumber')
                    order_number = order_number_elem.text.strip() if order_number_elem else "N/A"
                    
                    part_number_elem = item.select_one('.part-number a.text-link')
                    part_number = part_number_elem.text.strip() if part_number_elem else "N/A"
                    
                    description_elem = item.select_one('.column.describe')
                    description = description_elem.text.strip() if description_elem else "N/A"
                    
                    quantity_elem = item.select_one('.column.quantity')
                    quantity = quantity_elem.text.strip() if quantity_elem else "1"
                    
                    # Validation (scrapeandpush.py skip logic)
                    valid_part = "N/A" not in [order_number, part_number, description]
                    
                    if valid_part:
                        successful_extractions += 1
                    
                    part_data = {
                        "index": count + 1,
                        "call_out_order": order_number,
                        "part_number": part_number,
                        "usage_name": description,
                        "unit_qty": quantity,
                        "lr": orientation,
                        "remark": notes,
                        "valid": valid_part
                    }
                    
                    extracted_parts.append(part_data)
                    
                    # Show first few parts for verification
                    if count < 3:
                        status = "✅" if valid_part else "❌"
                        print(f"      {status} Part {count+1}: {order_number} | {part_number} | {description[:30]}...")
                        
                except Exception as e:
                    print(f"      💥 Part {count+1} extraction failed: {str(e)}")
            
            parsing_results["extraction_steps"]["parts_data"] = {
                "total_found": len(parts_items),
                "visible_count": len(filtered_items),
                "extracted_count": len(extracted_parts),
                "valid_count": successful_extractions,
                "invalid_count": len(extracted_parts) - successful_extractions,
                "method": "Complex multi-step extraction with validation"
            }
            
            print(f"      📊 Summary: {len(extracted_parts)} extracted, {successful_extractions} valid")
            
            return parsing_results
            
        except Exception as e:
            print(f"      💥 File parsing failed: {str(e)}")
            return {"error": str(e)}
    
    def simulate_scrapeandpush_flow(self, root_dir):
        """Simulate the complete scrapeandpush.py workflow"""
        
        print("\n🚀 SIMULATING SCRAPEANDPUSH.PY WORKFLOW")
        print("=" * 50)
        
        # Step 1: Directory traversal
        directory_structure = self.analyze_traversal_methodology(root_dir)
        
        # Step 2: Process each category (parent title creation)
        processing_results = {}
        
        for category_name, category_info in directory_structure.items():
            print(f"\n📦 PROCESSING CATEGORY: {category_name}")
            print(f"   Formatted name: {category_info['formatted_name']}")
            print(f"   Files to process: {category_info['html_files']}")
            
            # Process each HTML file in the category
            category_results = {}
            
            for html_file in category_info['html_files']:
                html_path = os.path.join(root_dir, category_name, html_file)
                
                print(f"\n   📄 Processing: {html_file}")
                parsing_result = self.analyze_html_parsing_pattern(html_path, category_name)
                category_results[html_file] = parsing_result
            
            processing_results[category_name] = category_results
        
        # Step 3: Generate summary
        self.generate_processing_summary(processing_results)
        
        return processing_results
    
    def generate_processing_summary(self, processing_results):
        """Generate summary of the processing results"""
        
        print(f"\n📊 PROCESSING SUMMARY")
        print("=" * 25)
        
        total_files = 0
        total_parts = 0
        total_valid_parts = 0
        total_svg_size = 0
        
        for category_name, category_results in processing_results.items():
            print(f"\n📂 {category_name}:")
            
            for html_file, result in category_results.items():
                if "error" not in result:
                    total_files += 1
                    
                    steps = result.get("extraction_steps", {})
                    
                    # Parts data
                    parts_info = steps.get("parts_data", {})
                    file_parts = parts_info.get("extracted_count", 0)
                    file_valid = parts_info.get("valid_count", 0)
                    
                    total_parts += file_parts
                    total_valid_parts += file_valid
                    
                    # SVG data
                    svg_info = steps.get("svg", {})
                    svg_size = svg_info.get("size", 0)
                    total_svg_size += svg_size
                    
                    print(f"   📄 {html_file}:")
                    print(f"      Title: {steps.get('title', {}).get('content', 'N/A')}")
                    print(f"      Parts: {file_parts} total, {file_valid} valid")
                    print(f"      SVG: {svg_size:,} characters")
                
                else:
                    print(f"   ❌ {html_file}: {result['error']}")
        
        print(f"\n🎯 OVERALL SUMMARY:")
        print(f"   Files processed: {total_files}")
        print(f"   Total parts extracted: {total_parts}")
        print(f"   Valid parts: {total_valid_parts}")
        print(f"   Total SVG content: {total_svg_size:,} characters")
        print(f"   Success rate: {(total_valid_parts/total_parts*100 if total_parts > 0 else 0):.1f}%")
        
        self.analysis["file_processing_stats"] = {
            "files_processed": total_files,
            "total_parts": total_parts,
            "valid_parts": total_valid_parts,
            "total_svg_size": total_svg_size,
            "success_rate": (total_valid_parts/total_parts*100 if total_parts > 0 else 0)
        }

def main():
    """Main analysis function"""
    
    print("🔬 SCRAPEANDPUSH.PY TRAVERSAL PATTERN ANALYSIS")
    print("=" * 60)
    
    # Define the sample data directory
    root_dir = r"c:\pythonstuff\vansdirect\epc_parts_store\epcdata\LSH14C4C5NA129710"
    
    # Initialize analyzer
    analyzer = TraversalPatternAnalyzer()
    
    # Run complete simulation
    results = analyzer.simulate_scrapeandpush_flow(root_dir)
    
    # Save analysis results
    output_file = "traversal_pattern_analysis.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "methodology_analysis": analyzer.analysis,
            "processing_results": results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Analysis saved to: {output_file}")
    
    print(f"\n🎓 KEY INSIGHTS FROM SCRAPEANDPUSH.PY:")
    print("=" * 45)
    print("1. Uses os.walk() for recursive directory traversal")
    print("2. Extracts serial number from root directory name")
    print("3. Processes only directories containing .html files")
    print("4. Creates parent titles from directory names (formatted)")
    print("5. Extracts child titles from HTML legend-title elements")
    print("6. Stores complete SVG markup as text for diagrams")
    print("7. Uses complex DOM selectors for parts data extraction")
    print("8. Validates parts data before database insertion")
    print("9. Handles L/R orientation and remarks separately")
    print("10. Skips hidden parts items (class contains 'dn')")

if __name__ == "__main__":
    main()
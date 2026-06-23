"""
Data Extraction Validation Script
Tests and validates the data extraction logic from HTML files
Mirrors the parsing logic in scrapeandpush.py for verification
"""

import os
from bs4 import BeautifulSoup
import json

class DataExtractionValidator:
    """Validates data extraction logic matching scrapeandpush.py"""
    
    def __init__(self):
        self.results = {
            "files_processed": 0,
            "successful_extractions": 0,
            "failed_extractions": 0,
            "extraction_details": {},
            "validation_errors": []
        }
    
    def validate_html_file(self, html_path):
        """Validate data extraction from a single HTML file"""
        
        print(f"\n🔍 Validating: {html_path}")
        print("-" * 50)
        
        try:
            with open(html_path, 'r', encoding='utf-8') as file:
                html = file.read()
            
            soup = BeautifulSoup(html, 'html.parser')
            
            validation_result = {
                "file_path": html_path,
                "success": False,
                "errors": [],
                "extracted_data": {}
            }
            
            # Test 1: Extract legend title (matches scrapeandpush.py logic)
            print("📝 Testing legend title extraction...")
            legend_title = soup.find('span', id='legend-title')
            if legend_title:
                title_content = legend_title.text.strip()
                validation_result["extracted_data"]["title"] = title_content
                print(f"   ✅ Title extracted: '{title_content}'")
            else:
                fallback_title = os.path.basename(html_path).replace('.html', '')
                validation_result["extracted_data"]["title"] = fallback_title
                validation_result["errors"].append("No legend-title found, using filename fallback")
                print(f"   ⚠️  No legend-title, using fallback: '{fallback_title}'")
            
            # Test 2: Extract SVG content (matches scrapeandpush.py logic)
            print("🎨 Testing SVG extraction...")
            svg_element = soup.find('svg', attrs={"xmlns": "http://www.w3.org/2000/svg"})
            if svg_element:
                svg_content = str(svg_element)
                validation_result["extracted_data"]["svg_length"] = len(svg_content)
                print(f"   ✅ SVG extracted: {len(svg_content):,} characters")
            else:
                validation_result["extracted_data"]["svg_length"] = 0
                validation_result["errors"].append("No SVG element found")
                print(f"   ❌ No SVG element found")
            
            # Test 3: Extract orientation and remarks (extra info)
            print("📊 Testing extra info extraction...")
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
                
                validation_result["extracted_data"]["extra_info_count"] = len(extra)
                print(f"   ✅ Extra info entries: {len(extra)}")
                
            except Exception as e:
                validation_result["errors"].append(f"Extra info extraction error: {str(e)}")
                print(f"   ⚠️  Extra info extraction error: {str(e)}")
            
            # Test 4: Extract main parts data (matches scrapeandpush.py logic)
            print("🔧 Testing parts data extraction...")
            parts_items = soup.find_all(lambda tag: tag.name == "div" and 
                                      "parts-item" in tag.get("class", []) and 
                                      tag.has_attr("data-callout"))
            
            filtered_items = [item for item in parts_items if 'dn' not in item.get('class', [])]
            
            print(f"   📋 Found {len(parts_items)} total parts items")
            print(f"   👁️  Found {len(filtered_items)} visible parts items")
            
            extracted_parts = []
            count = 0
            
            for item in filtered_items:
                try:
                    # Get orientation and notes from extra if available
                    orientation = extra[count]['orientation'] if count < len(extra) else "N/A"
                    notes = extra[count]['remark'] if count < len(extra) else "N/A"
                    
                    # Extract all the other fields (matching scrapeandpush.py exactly)
                    order_number_elem = item.select_one('.column.ordernumber')
                    order_number = order_number_elem.text.strip() if order_number_elem else "N/A"
                    
                    part_number_elem = item.select_one('.part-number a.text-link')
                    part_number = part_number_elem.text.strip() if part_number_elem else "N/A"
                    
                    description_elem = item.select_one('.column.describe')
                    description = description_elem.text.strip() if description_elem else "N/A"
                    
                    quantity_elem = item.select_one('.column.quantity')
                    quantity = quantity_elem.text.strip() if quantity_elem else "1"
                    
                    # Data validation
                    valid_part = True
                    if "N/A" in [order_number, part_number, description]:
                        valid_part = False
                    
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
                    count += 1
                    
                    # Print first few parts for verification
                    if count <= 3:
                        status = "✅" if valid_part else "⚠️"
                        print(f"   {status} Part {count}: {part_number} - {description[:40]}...")
                    
                except Exception as e:
                    validation_result["errors"].append(f"Part {count + 1} extraction error: {str(e)}")
                    print(f"   ❌ Part {count + 1} extraction error: {str(e)}")
                    count += 1
            
            validation_result["extracted_data"]["parts"] = extracted_parts
            validation_result["extracted_data"]["valid_parts_count"] = sum(1 for p in extracted_parts if p["valid"])
            validation_result["extracted_data"]["invalid_parts_count"] = sum(1 for p in extracted_parts if not p["valid"])
            
            print(f"   📊 Total parts extracted: {len(extracted_parts)}")
            print(f"   ✅ Valid parts: {validation_result['extracted_data']['valid_parts_count']}")
            print(f"   ⚠️  Invalid parts: {validation_result['extracted_data']['invalid_parts_count']}")
            
            # Overall validation success
            if legend_title and len(extracted_parts) > 0:
                validation_result["success"] = True
                self.results["successful_extractions"] += 1
                print(f"   🎉 VALIDATION SUCCESSFUL")
            else:
                validation_result["errors"].append("Critical extraction failures")
                self.results["failed_extractions"] += 1
                print(f"   💥 VALIDATION FAILED")
            
            self.results["files_processed"] += 1
            return validation_result
            
        except Exception as e:
            validation_result = {
                "file_path": html_path,
                "success": False,
                "errors": [f"File processing error: {str(e)}"],
                "extracted_data": {}
            }
            self.results["failed_extractions"] += 1
            self.results["files_processed"] += 1
            print(f"   💥 FILE PROCESSING ERROR: {str(e)}")
            return validation_result
    
    def validate_directory(self, root_path):
        """Validate all HTML files in the directory structure"""
        
        print("🧪 DATA EXTRACTION VALIDATION")
        print("=" * 50)
        print(f"Root Directory: {root_path}")
        print(f"Vehicle Serial: {os.path.basename(root_path)}")
        
        # Walk through directory and validate each HTML file
        for root, dirs, files in os.walk(root_path):
            html_files = [f for f in files if f.endswith('.html')]
            
            if html_files:
                category = os.path.basename(root)
                print(f"\n📁 Processing Category: {category}")
                
                for html_file in html_files:
                    html_path = os.path.join(root, html_file)
                    validation_result = self.validate_html_file(html_path)
                    self.results["extraction_details"][f"{category}/{html_file}"] = validation_result
        
        # Print summary
        print(f"\n📊 VALIDATION SUMMARY")
        print("=" * 25)
        print(f"Files Processed: {self.results['files_processed']}")
        print(f"Successful Extractions: {self.results['successful_extractions']}")
        print(f"Failed Extractions: {self.results['failed_extractions']}")
        
        success_rate = (self.results['successful_extractions'] / self.results['files_processed'] * 100) if self.results['files_processed'] > 0 else 0
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Print detailed results for each file
        print(f"\n📋 DETAILED RESULTS")
        print("-" * 20)
        
        for file_key, result in self.results["extraction_details"].items():
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"{status} {file_key}")
            
            if result.get("extracted_data"):
                data = result["extracted_data"]
                print(f"   Title: {data.get('title', 'N/A')}")
                print(f"   SVG: {data.get('svg_length', 0):,} chars")
                print(f"   Parts: {len(data.get('parts', []))}")
                print(f"   Valid: {data.get('valid_parts_count', 0)}")
            
            if result.get("errors"):
                for error in result["errors"]:
                    print(f"   ⚠️  {error}")
            print()
        
        return self.results

def main():
    """Main validation function"""
    
    # Initialize validator
    validator = DataExtractionValidator()
    
    # Define path to validate
    root_path = r"c:\pythonstuff\vansdirect\epc_parts_store\epcdata\LSH14C4C5NA129710"
    
    # Run validation
    results = validator.validate_directory(root_path)
    
    # Save results to JSON
    output_file = "extraction_validation.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Validation results saved to: {output_file}")
    
    # Final recommendation
    if results['successful_extractions'] == results['files_processed']:
        print(f"\n🎯 RECOMMENDATION: Ready for production processing!")
        print(f"All {results['files_processed']} files validated successfully.")
    else:
        print(f"\n⚠️  RECOMMENDATION: Review failed extractions before processing.")
        print(f"Only {results['successful_extractions']}/{results['files_processed']} files validated successfully.")

if __name__ == "__main__":
    main()
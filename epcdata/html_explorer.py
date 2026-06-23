"""
HTML Structure Explorer
Interactive tool to explore and understand the HTML structure of vehicle parts files
"""

import os
from bs4 import BeautifulSoup, Comment
import json

class HTMLStructureExplorer:
    """Explore HTML structure and content for understanding data layout"""
    
    def __init__(self):
        self.exploration_results = {}
    
    def explore_html_structure(self, html_path):
        """Explore the structure of an HTML file in detail"""
        
        print(f"\n🔍 EXPLORING HTML STRUCTURE")
        print(f"File: {html_path}")
        print("=" * 60)
        
        try:
            with open(html_path, 'r', encoding='utf-8') as file:
                html_content = file.read()
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            exploration = {
                "file_info": {
                    "path": html_path,
                    "size_bytes": len(html_content),
                    "size_mb": len(html_content) / 1024 / 1024
                },
                "structure_analysis": {},
                "key_elements": {},
                "parts_table_structure": {},
                "svg_analysis": {}
            }
            
            # Basic structure analysis
            print("📋 BASIC STRUCTURE")
            print("-" * 20)
            
            all_tags = soup.find_all()
            tag_counts = {}
            for tag in all_tags:
                tag_name = tag.name
                tag_counts[tag_name] = tag_counts.get(tag_name, 0) + 1
            
            exploration["structure_analysis"]["total_elements"] = len(all_tags)
            exploration["structure_analysis"]["unique_tags"] = len(tag_counts)
            exploration["structure_analysis"]["tag_distribution"] = dict(sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10])
            
            print(f"Total HTML elements: {len(all_tags):,}")
            print(f"Unique tag types: {len(tag_counts)}")
            print(f"Most common tags: {list(exploration['structure_analysis']['tag_distribution'].keys())[:5]}")
            
            # Find key structural elements
            print(f"\n🎯 KEY ELEMENTS")
            print("-" * 15)
            
            # Legend title
            legend_title = soup.find('span', id='legend-title')
            if legend_title:
                exploration["key_elements"]["legend_title"] = legend_title.text.strip()
                print(f"Legend Title: '{legend_title.text.strip()}'")
            
            # Main containers
            containers = soup.find_all('div', class_='condition-entity')
            exploration["key_elements"]["main_containers"] = len(containers)
            print(f"Main containers (.condition-entity): {len(containers)}")
            
            # Parts table structure
            parts_tables = soup.find_all('div', class_='parts-table-wrapper')
            exploration["key_elements"]["parts_tables"] = len(parts_tables)
            print(f"Parts tables (.parts-table-wrapper): {len(parts_tables)}")
            
            # SVG analysis
            print(f"\n🎨 SVG ANALYSIS")
            print("-" * 15)
            
            svgs = soup.find_all('svg')
            exploration["svg_analysis"]["svg_count"] = len(svgs)
            print(f"SVG elements found: {len(svgs)}")
            
            if svgs:
                main_svg = svgs[0]  # Assume first SVG is the main diagram
                exploration["svg_analysis"]["attributes"] = dict(main_svg.attrs)
                
                # Count SVG child elements
                svg_children = main_svg.find_all()
                svg_tag_counts = {}
                for child in svg_children:
                    tag_name = child.name
                    svg_tag_counts[tag_name] = svg_tag_counts.get(tag_name, 0) + 1
                
                exploration["svg_analysis"]["child_elements"] = len(svg_children)
                exploration["svg_analysis"]["child_tag_distribution"] = svg_tag_counts
                
                print(f"SVG dimensions: {main_svg.get('width')} x {main_svg.get('height')}")
                print(f"SVG child elements: {len(svg_children)}")
                print(f"SVG child tags: {list(svg_tag_counts.keys())[:5]}")
            
            # Parts data analysis
            print(f"\n🔧 PARTS DATA ANALYSIS")
            print("-" * 25)
            
            # Find all parts items
            all_parts_items = soup.find_all('div', class_='parts-item')
            visible_parts = [item for item in all_parts_items if 'dn' not in item.get('class', [])]
            hidden_parts = [item for item in all_parts_items if 'dn' in item.get('class', [])]
            
            exploration["parts_table_structure"]["total_parts"] = len(all_parts_items)
            exploration["parts_table_structure"]["visible_parts"] = len(visible_parts)
            exploration["parts_table_structure"]["hidden_parts"] = len(hidden_parts)
            
            print(f"Total parts items: {len(all_parts_items)}")
            print(f"Visible parts: {len(visible_parts)}")
            print(f"Hidden parts (.dn): {len(hidden_parts)}")
            
            # Analyze part item structure
            if visible_parts:
                sample_part = visible_parts[0]
                part_columns = sample_part.find_all('span', class_='column')
                
                exploration["parts_table_structure"]["columns_per_part"] = len(part_columns)
                exploration["parts_table_structure"]["column_classes"] = []
                
                print(f"Columns per part: {len(part_columns)}")
                print(f"Sample part structure:")
                
                for i, col in enumerate(part_columns):
                    col_classes = ' '.join(col.get('class', []))
                    col_text = col.text.strip()[:30] + '...' if len(col.text.strip()) > 30 else col.text.strip()
                    exploration["parts_table_structure"]["column_classes"].append(col_classes)
                    print(f"   Column {i+1}: .{col_classes} = '{col_text}'")
                
                # Special analysis for data attributes
                data_attrs = {k: v for k, v in sample_part.attrs.items() if k.startswith('data-')}
                exploration["parts_table_structure"]["data_attributes"] = data_attrs
                print(f"Data attributes: {list(data_attrs.keys())}")
            
            # Class analysis
            print(f"\n🏷️  CSS CLASS ANALYSIS")
            print("-" * 20)
            
            class_usage = {}
            for element in soup.find_all(class_=True):
                for class_name in element.get('class', []):
                    class_usage[class_name] = class_usage.get(class_name, 0) + 1
            
            top_classes = dict(sorted(class_usage.items(), key=lambda x: x[1], reverse=True)[:10])
            exploration["structure_analysis"]["top_css_classes"] = top_classes
            
            print(f"Most used CSS classes:")
            for class_name, count in list(top_classes.items())[:5]:
                print(f"   .{class_name}: {count} uses")
            
            # Look for specific data patterns
            print(f"\n🔍 DATA PATTERNS")
            print("-" * 15)
            
            # Part numbers pattern
            part_links = soup.find_all('a', class_='text-link')
            part_numbers = [link.text.strip() for link in part_links if link.get('href', '').startswith('/part/')]
            exploration["key_elements"]["unique_part_numbers"] = len(set(part_numbers))
            print(f"Unique part numbers: {len(set(part_numbers))}")
            
            # Callout numbers
            callout_elements = soup.find_all('span', class_='column ordernumber')
            callouts = [elem.text.strip() for elem in callout_elements if elem.text.strip().isdigit()]
            if callouts:
                exploration["key_elements"]["callout_range"] = f"{min(callouts)} - {max(callouts)}"
                print(f"Callout number range: {min(callouts)} to {max(callouts)}")
            
            return exploration
            
        except Exception as e:
            print(f"❌ Error exploring {html_path}: {str(e)}")
            return {"error": str(e)}
    
    def compare_html_files(self, html_paths):
        """Compare structure across multiple HTML files"""
        
        print(f"\n📊 COMPARATIVE ANALYSIS")
        print("=" * 30)
        
        comparisons = {}
        
        for html_path in html_paths:
            file_name = os.path.basename(html_path)
            exploration = self.explore_html_structure(html_path)
            comparisons[file_name] = exploration
            
            print(f"\n" + "="*60)  # Separator between files
        
        # Summary comparison
        print(f"\n📋 COMPARISON SUMMARY")
        print("-" * 25)
        
        for file_name, data in comparisons.items():
            if "error" not in data:
                print(f"\n{file_name}:")
                print(f"   File Size: {data['file_info']['size_mb']:.2f} MB")
                print(f"   Total Elements: {data['structure_analysis']['total_elements']:,}")
                print(f"   Parts Items: {data.get('parts_table_structure', {}).get('total_parts', 0)}")
                print(f"   Visible Parts: {data.get('parts_table_structure', {}).get('visible_parts', 0)}")
                print(f"   SVG Elements: {data.get('svg_analysis', {}).get('svg_count', 0)}")
        
        return comparisons

def main():
    """Main exploration function"""
    
    # Initialize explorer
    explorer = HTMLStructureExplorer()
    
    # Define files to explore
    root_path = r"c:\pythonstuff\vansdirect\epc_parts_store\epcdata\LSH14C4C5NA129710"
    
    html_files = []
    for root, dirs, files in os.walk(root_path):
        for file in files:
            if file.endswith('.html'):
                html_files.append(os.path.join(root, file))
    
    print("🔬 HTML STRUCTURE EXPLORER")
    print("=" * 50)
    print(f"Found {len(html_files)} HTML files to explore")
    
    # Option to explore all files or just one
    if len(html_files) == 1:
        # Single file exploration
        results = explorer.explore_html_structure(html_files[0])
    else:
        # Multiple file comparison
        print(f"\n🆚 COMPARING {len(html_files)} FILES")
        results = explorer.compare_html_files(html_files)
    
    # Save results
    output_file = "html_structure_exploration.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Exploration results saved to: {output_file}")
    
    # Interactive features
    print(f"\n🤖 QUICK INSIGHTS")
    print("-" * 15)
    
    if isinstance(results, dict) and "error" not in results:
        if "parts_table_structure" in results:
            # Single file results
            parts_data = results["parts_table_structure"]
            print(f"✅ This file contains {parts_data.get('visible_parts', 0)} extractable parts")
            print(f"✅ Parts data is structured with {parts_data.get('columns_per_part', 0)} columns per part")
            print(f"✅ Ready for scrapeandpush.py processing")
        else:
            # Multiple file results
            total_parts = sum(data.get('parts_table_structure', {}).get('visible_parts', 0) 
                             for data in results.values() if 'error' not in data)
            print(f"✅ Total extractable parts across all files: {total_parts}")
            print(f"✅ All files appear ready for scrapeandpush.py processing")

if __name__ == "__main__":
    main()
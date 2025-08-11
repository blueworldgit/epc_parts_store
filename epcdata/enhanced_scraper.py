#!/usr/bin/env python
"""
Enhanced scraper that converts SVG to images during import
"""
import os
import sys
import django
from bs4 import BeautifulSoup
import logging
from io import BytesIO
import base64

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from motorpartsdata.serializers import (
    SerialNumberSerializer,
    ParentTitleSerializer,
    ChildTitleSerializer,
    PartSerializer
)
from vehicle_utils import determine_vehicle_brand

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("enhanced_scraper.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SVGImageCreator:
    """Handle SVG to image conversion during scraping"""
    
    def __init__(self):
        self.has_cairosvg = self._check_cairosvg()
    
    def _check_cairosvg(self):
        """Check if cairosvg is available"""
        try:
            import cairosvg
            return True
        except ImportError:
            logger.warning("cairosvg not available. SVG will be stored as text only.")
            return False
    
    def process_svg(self, svg_content, part_number):
        """Process SVG content and optionally convert to image"""
        processed_data = {
            'svg_content': svg_content,
            'image_data': None,
            'image_format': None
        }
        
        if self.has_cairosvg and svg_content:
            try:
                import cairosvg
                from PIL import Image
                
                # Convert SVG to PNG
                png_data = cairosvg.svg2png(
                    bytestring=svg_content.encode('utf-8'),
                    output_width=800,
                    output_height=600
                )
                
                # Encode as base64 for storage
                processed_data['image_data'] = base64.b64encode(png_data).decode('utf-8')
                processed_data['image_format'] = 'PNG'
                
                logger.info(f"Converted SVG to PNG for part: {part_number}")
                
            except Exception as e:
                logger.warning(f"Failed to convert SVG for {part_number}: {str(e)}")
        
        return processed_data
    
    def save_image_file(self, image_data, part_number, media_root):
        """Save image data to file system"""
        if not image_data:
            return None
        
        try:
            # Create images directory if it doesn't exist
            images_dir = os.path.join(media_root, 'part_diagrams')
            os.makedirs(images_dir, exist_ok=True)
            
            # Decode base64 image data
            image_bytes = base64.b64decode(image_data)
            
            # Save to file
            filename = f"{part_number}_diagram.png"
            file_path = os.path.join(images_dir, filename)
            
            with open(file_path, 'wb') as f:
                f.write(image_bytes)
            
            # Return relative path for storage in database
            return f"part_diagrams/{filename}"
            
        except Exception as e:
            logger.error(f"Failed to save image for {part_number}: {str(e)}")
            return None

def process_html_file_enhanced(html_path, serial_instance, parent_instance, svg_processor):
    """Enhanced HTML processing with SVG image creation"""
    try:
        logger.info(f"Processing file: {html_path}")
        
        with open(html_path, 'r', encoding='utf-8') as file:
            html = file.read()
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract the title from legend-title
        legend_title = soup.find('span', id='legend-title')
        title_content = legend_title.text.strip() if legend_title else os.path.basename(html_path).replace('.html', '')
        
        # Extract SVG code
        svg_element = soup.find('svg', attrs={"xmlns": "http://www.w3.org/2000/svg"})
        svg_content = str(svg_element) if svg_element else "<svg></svg>"
        
        # Process SVG for image creation
        svg_data = svg_processor.process_svg(svg_content, title_content)
        
        # Create child title record with enhanced SVG data
        child_data = {
            "title": title_content,
            "parent": parent_instance.id,
            "svg_code": svg_content,  # Keep original SVG
        }
        
        child_serializer = ChildTitleSerializer(data=child_data)
        if child_serializer.is_valid():
            child_instance = child_serializer.save()
            logger.info(f"Created child title: {title_content}")
            
            # Save image file if conversion was successful
            if svg_data['image_data']:
                from django.conf import settings
                image_path = svg_processor.save_image_file(
                    svg_data['image_data'], 
                    title_content.replace(' ', '_'), 
                    settings.MEDIA_ROOT
                )
                if image_path:
                    logger.info(f"Saved diagram image: {image_path}")
            
            # Continue with parts processing (same as your original logic)
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
            except Exception as e:
                logger.warning(f"Error extracting extra info: {str(e)}")
            
            # Process parts (rest of your original logic)
            parts_items = soup.find_all(lambda tag: tag.name == "div" and 
                                    "parts-item" in tag.get("class", []) and 
                                    tag.has_attr("data-callout"))
            
            filtered_items = [item for item in parts_items if 'dn' not in item.get('class', [])]
            count = 0
            
            for item in filtered_items:
                try:
                    orientation = extra[count]['orientation'] if count < len(extra) else "N/A"
                    notes = extra[count]['remark'] if count < len(extra) else "N/A"
                    
                    order_number_elem = item.select_one('.column.ordernumber')
                    order_number = order_number_elem.text.strip() if order_number_elem else "N/A"
                    
                    part_number_elem = item.select_one('.part-number a.text-link')
                    part_number = part_number_elem.text.strip() if part_number_elem else "N/A"
                    
                    description_elem = item.select_one('.column.describe')
                    description = description_elem.text.strip() if description_elem else "N/A"
                    
                    quantity_elem = item.select_one('.column.quantity')
                    quantity = quantity_elem.text.strip() if quantity_elem else "1"
                    
                    if "N/A" in [order_number, part_number, description]:
                        continue
                    
                    part_data = {
                        "child_title": child_instance.id,
                        "call_out_order": int(order_number) if order_number.isdigit() else count + 1,
                        "part_number": part_number,
                        "usage_name": description,
                        "unit_qty": quantity,
                        "lr": orientation,
                        "remark": notes,
                        "nn_note": "",
                    }

                    count += 1
                    
                    part_serializer = PartSerializer(data=part_data)
                    if part_serializer.is_valid():
                        part_serializer.save()
                        logger.info(f"Created part: {part_data['part_number']} - {part_data['usage_name']}")
                    else:
                        logger.error(f"Part serializer errors: {part_serializer.errors}")
                        
                except Exception as e:
                    logger.warning(f"Error processing part {count}: {str(e)}")
        else:
            logger.error(f"Child title serializer errors: {child_serializer.errors}")
    
    except Exception as e:
        logger.error(f"Error processing {html_path}: {str(e)}")

def process_directory_enhanced(root_dir):
    """Enhanced directory processing with SVG image creation"""
    svg_processor = SVGImageCreator()
    
    try:
        serial_name = os.path.basename(root_dir)
        vehicle_brand = determine_vehicle_brand(serial_name)
        
        serial_data = {
            "serial": serial_name,
            "vehicle_brand": vehicle_brand
        }
        
        from motorpartsdata.models import SerialNumber
        existing_serial = SerialNumber.objects.filter(serial=serial_name).first()
        
        if existing_serial:
            logger.info(f"Serial number {serial_name} already exists, using it")
            if existing_serial.vehicle_brand != vehicle_brand:
                existing_serial.vehicle_brand = vehicle_brand
                existing_serial.save()
                logger.info(f"Updated vehicle brand for {serial_name} to {vehicle_brand}")
            serial_instance = existing_serial
        else:
            serial_serializer = SerialNumberSerializer(data=serial_data)
            if serial_serializer.is_valid():
                serial_instance = serial_serializer.save()
                logger.info(f"Created serial number: {serial_data['serial']} for brand: {vehicle_brand}")
            else:
                logger.error(f"Serial number serializer errors: {serial_serializer.errors}")
                return
        
        for dirpath, dirnames, filenames in os.walk(root_dir):
            relative_path = os.path.relpath(dirpath, root_dir)
            
            if relative_path == '.':
                continue
                
            html_files = [f for f in filenames if f.lower().endswith('.html')]
            if html_files:
                parent_name = os.path.basename(dirpath)
                parent_name = parent_name.replace('_', ' ').title()
                
                parent_data = {
                    "title": parent_name,
                    "serial_number": serial_instance.id
                }
                
                from motorpartsdata.models import ParentTitle
                existing_parent = ParentTitle.objects.filter(
                    title=parent_name, 
                    serial_number=serial_instance
                ).first()
                
                if existing_parent:
                    logger.info(f"Parent title {parent_name} already exists, using it")
                    parent_instance = existing_parent
                else:
                    parent_serializer = ParentTitleSerializer(data=parent_data)
                    if parent_serializer.is_valid():
                        parent_instance = parent_serializer.save()
                        logger.info(f"Created parent title: {parent_data['title']}")
                    else:
                        logger.error(f"Parent title serializer errors: {parent_serializer.errors}")
                        continue
                
                for filename in html_files:
                    file_path = os.path.join(dirpath, filename)
                    process_html_file_enhanced(file_path, serial_instance, parent_instance, svg_processor)
    
    except Exception as e:
        logger.error(f"Error processing directory {root_dir}: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        root_directory = sys.argv[1]
        logger.info(f"Starting enhanced processing for directory: {root_directory}")
        process_directory_enhanced(root_directory)
        logger.info("Enhanced processing complete")
    else:
        logger.error("Please provide the root directory path as an argument")
        print("Usage: python enhanced_scraper.py /path/to/root/directory")

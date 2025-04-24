import os
import sys
import django
from bs4 import BeautifulSoup
import logging




# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("test_scraper.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')

# Setup Django
django.setup()

# Import your serializers
from motorpartsdata.serializers import (
    SerialNumberSerializer,
    ParentTitleSerializer,
    ChildTitleSerializer,
    PartSerializer
)

def process_html_file(html_path, serial_instance, parent_instance):
    """Process an HTML file using your existing BeautifulSoup parsing logic"""
    try:
        logger.info(f"Processing file: {html_path}")
        
        with open(html_path, 'r', encoding='utf-8') as file:
            html = file.read()
        
        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract the title from legend-title
        legend_title = soup.find('span', id='legend-title')
        title_content = legend_title.text.strip() if legend_title else os.path.basename(html_path).replace('.html', '')

        
        
        # Extract SVG code
        svg_element = soup.find('svg', attrs={"xmlns": "http://www.w3.org/2000/svg"})
        svg_content = str(svg_element) if svg_element else "<svg></svg>"
        
        # Debug SVG content
        logger.info(f"SVG found: {'Yes' if svg_element else 'No'}")
        
        # Create child title record
        child_data = {
            "title": title_content,
            "parent": parent_instance.id,
            "svg_code": svg_content,
        }
        
        child_serializer = ChildTitleSerializer(data=child_data)
        if child_serializer.is_valid():
            child_instance = child_serializer.save()
            logger.info(f"Created child title: {title_content}")
            
            # Now we'll extract the extra information first, but with more debug info
            container = soup.find('div', class_='condition-entity')
            logger.debug(f"Found container: {'Yes' if container else 'No'}")
            
            parts_table_rows = []
            orientation_data = []

            
            
            if container:
                # This is the section where your original code was looking for the orientation/LR values
                right_div = container.find('div', class_='parts-table-tbody parts-table-tbody-dflz')
                logger.debug(f"Found right_div: {'Yes' if right_div else 'No'}")
                
                if right_div:
                    right_rows = right_div.find_all('div', class_='parts-item')
                    filtered_items = [item for item in right_rows if 'dn' not in item.get('class', [])]
                    
                    for item in filtered_items:
                        # Print the HTML of each item to debug
                        logger.debug(f"Parts item HTML: {item}")
                        
                        # Try more generic selectors for orientation/LR 
                        
                        first_column = item.find(lambda tag: tag.name == "span" and tag.get("class") == ["column"])
                        orientation = first_column.text.strip() if first_column else "N/A"

                        #print(f"***Orientation***: {orientation}")

                        
                        
                        note_column = item.select_one('.text-column-note span')
                        remark = note_column.text.strip() if note_column else "N/A"

                        logger.debug(f"Found orientation: {orientation}")
                        
                        # Try different ways to get the remark
                        note_column = item.select_one('.text-column-note span')
                        
                        
                        remark = note_column.text.strip() if note_column else "N/A"
                        logger.debug(f"Found remark: {remark}")
                        
                        orientation_data.append({
                            'orientation': orientation,
                            'remark': remark
                        })
            
            # Now get the parts data
            parts_items = soup.find_all(lambda tag: tag.name == "div" and 
                                    "parts-item" in tag.get("class", []) and 
                                    tag.has_attr("data-callout"))
            
            filtered_items = [item for item in parts_items if 'dn' not in item.get('class', [])]
            
            logger.info(f"Found {len(filtered_items)} parts items and {len(orientation_data)} orientation items")
            
            count=0
            #print(orientation_data)
            for item in filtered_items:
                try:
                    # Get orientation and notes from the orientation_data if available
                    lr_value = orientation_data[count]['orientation'] 
                    remark_value = orientation_data[count]['remark']  
                    
                  
                    #print(f"***************orientation: {lr_value}")
                    # Log values for debugging
                    #logger.info(f"Part {count+1}: LR={lr_value}, Remark={remark_value}")
                    
                  
                    
                    # Extract all the other fields
                    order_number_elem = item.select_one('.column.ordernumber')
                    order_number = order_number_elem.text.strip() if order_number_elem else ""
                    
                    part_number_elem = item.select_one('.part-number a.text-link')
                    part_number = part_number_elem.text.strip() if part_number_elem else ""
                    
                    description_elem = item.select_one('.column.describe')
                    description = description_elem.text.strip() if description_elem else ""
                    
                    quantity_elem = item.select_one('.column.quantity')
                    quantity = quantity_elem.text.strip()
                    
                    # Skip this item if any required field is empty
                    
                    
                    # Create part record
                    part_data = {
                        "child_title": child_instance.id,
                        "call_out_order": int(order_number) if order_number.isdigit() else count + 1,
                        "part_number": part_number,
                        "usage_name": description,
                        "unit_qty": quantity,
                        "lr": lr_value,  # Use the fixed value
                        "remark": remark_value,  # Use the fixed value
                        "nn_note": "",  # You can add note handling if needed
                    }
                    print("***********************************")
                    print(part_data)
                    print("_______")
                    print(f"lr is {lr_value}")
                    print("***********************************")
                    
                    logger.info(f"Creating part with data: {part_data}")

                    count+=1
                    
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


def test_single_folder(root_dir, folder_name):
    """Process just a single folder for testing"""
    try:
        # Find the specific folder
        folder_path = None
        for dirpath, dirnames, filenames in os.walk(root_dir):
            if os.path.basename(dirpath) == folder_name:
                folder_path = dirpath
                break
        
        if not folder_path:
            logger.error(f"Folder '{folder_name}' not found in {root_dir}")
            return
            
        logger.info(f"Processing folder: {folder_path}")
        
        # Extract serial number from the root directory name
        serial_name = os.path.basename(root_dir)
        serial_data = {"serial": serial_name}
        
        # Check if this serial already exists
        from motorpartsdata.models import SerialNumber
        existing_serial = SerialNumber.objects.filter(serial=serial_name).first()
        
        if existing_serial:
            logger.info(f"Serial number {serial_name} already exists, using it")
            serial_instance = existing_serial
        else:
            serial_serializer = SerialNumberSerializer(data=serial_data)
            if serial_serializer.is_valid():
                serial_instance = serial_serializer.save()
                logger.info(f"Created serial number: {serial_data['serial']}")
            else:
                logger.error(f"Serial number serializer errors: {serial_serializer.errors}")
                return
        
        # Create parent title for the folder
        parent_name = folder_name
        # Replace underscores and handle other formatting if needed
        parent_name = parent_name.replace('_', ' ').title()
        
        parent_data = {
            "title": parent_name,
            "serial_number": serial_instance.id
        }
        
        # Check if this parent already exists
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
                return
        
        # Process HTML files in this directory
        html_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.html')]
        for filename in html_files:
            file_path = os.path.join(folder_path, filename)
            process_html_file(file_path, serial_instance, parent_instance)
    
    except Exception as e:
        logger.error(f"Error processing folder {folder_name}: {str(e)}")


if __name__ == "__main__":
    if len(sys.argv) > 2:
        root_directory = sys.argv[1]
        folder_name = sys.argv[2]
        logger.info(f"Testing single folder: {folder_name} in {root_directory}")
        test_single_folder(root_directory, folder_name)
        logger.info("Processing complete")
    else:
        logger.error("Please provide the root directory path and folder name as arguments")
        print("Usage: python test_scraper.py /path/to/root/directory folder_name")
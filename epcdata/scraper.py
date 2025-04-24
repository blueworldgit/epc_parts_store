from bs4 import BeautifulSoup

# Your HTML string

with open('./LSH14C4C5NA129710/rear lamp/RearLamp.html', 'r', encoding='utf-8') as file:
    html = file.read()

# Parse the HTML
soup = BeautifulSoup(html, 'html.parser')

legend_title = soup.find('span', id='legend-title')


title_content = legend_title.text.strip() if legend_title else "Not found"

"title_content is title var from the ChildTitle model"


svg_element = soup.find('svg', attrs={"xmlns": "http://www.w3.org/2000/svg"})


if svg_element:
    # Get the complete SVG as a string
    svg_content = str(svg_element)

"svg_content is svg_code var from the ChildTitle model"

#print(svg_content)

container = soup.find('div', class_='condition-entity') 

right_div = container.find('div', class_='parts-table-tbody parts-table-tbody-dflz')

right_rows = right_div.find_all('div', class_='parts-item')
""" 
print("-------------------------------------------")

print(right_rows)
print("--------------------------------------------") """



filtered_items = [item for item in right_rows if 'dn' not in item.get('class', [])]
extra = []
for item in filtered_items:

    first_column = item.find(lambda tag: tag.name == "span" and tag.get("class") == ["column"])
    orientation = first_column.text.strip() if first_column else "N/A"

    #print(first_content)
    
    # Extract the *** from the text-column-note span
    note_column = item.select_one('.text-column-note span')
    #print(note_column)
    remark = remark = note_column.text.strip() if note_column else "N/A"

    #print(note_content)

    extra.append({
    
    'orientation' :orientation,
    'remark' :remark

})
    

    


parts_items = soup.find_all(lambda tag: tag.name == "div" and 
                           "parts-item" in tag.get("class", []) and 
                           tag.has_attr("data-callout"))


filtered_items = [item for item in parts_items if 'dn' not in item.get('class', [])]



# Extract the data you want from each item
parts_data = []
count=0;

for item in filtered_items:

   
    orientation=extra[count]['orientation'];
    notes=extra[count]['remark'];

    
    first_column = item.find(lambda tag: tag.name == "span" and tag.get("class") == ["column"])
    first_content = first_column.text.strip() if first_column else "N/A"

    #print(first_content)
    
    # Extract the *** from the text-column-note span
    note_column = item.select_one('.text-column-note span')
    note_content = note_column.get('title', '').strip() if note_column else "N/A"
   
    # Get order number from the ordernumber span
    order_number_elem = item.select_one('.column.ordernumber')
    order_number = order_number_elem.text.strip() if order_number_elem else "N/A"
    
    # Get part number from the link text within part-number div
    part_number_elem = item.select_one('.part-number a.text-link')
    part_number = part_number_elem.text.strip() if part_number_elem else "N/A"
    
    # Get description from the describe span
    description_elem = item.select_one('.column.describe')
    description = description_elem.text.strip() if description_elem else "N/A"
    
    # Get quantity from the quantity span
    quantity_elem = item.select_one('.column.quantity')
    quantity = quantity_elem.text.strip() if quantity_elem else "N/A"
    
    # Skip this item if any field has "N/A"
    if "N/A" in [order_number, part_number, description, quantity]:
        continue

    #print(first_content)
    
    parts_data.append({
        'order_number': order_number,
        'part_number': part_number,
        'description': description,
        'quantity': quantity,
        'orientation' :orientation,
        'remark' :notes,
        

    })

    count+=1

# Print the extracted data
for part in parts_data:
    print("------------------------------------------------------------------------------")
    print(f"Order Number: {part['order_number']}")
    print(f"Part Number: {part['part_number']}")
    print(f"Description: {part['description']}")
    print(f"Quantity: {part['quantity']}")
    print(f"orientation: {part['orientation']}")
    print(f"remark: {part['remark']}")
    print("------------------------------------------------------------------------------")

    #print("-" * 40)

""" print(extra) """
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pynput import keyboard
import time
import traceback
from bs4 import BeautifulSoup

# Initialize data storage
collected_html_sections = []

# Set up browser (NOT headless so you can see and interact with it)
options = Options()
options.add_experimental_option("detach", True)  # Keeps browser open
driver = webdriver.Chrome(options=options)

# Navigate to login page
login_url = "https://epc.saicmaxus.com/"  # Replace with your actual login URL
driver.get(login_url)

# Prompt user to manually login
print("Please log in manually in the browser window...")
input("Press Enter when you've logged in successfully...")

print("Login successful! Now you can navigate the site.")
print("- Press 's' to save current page's legend-parts section")
print("- Press 'd' to debug page elements")
print("- Press 'q' to save all data and quit the script")

# Function to save current page section with debugging
def save_current_page():
    print("Checking for new tabs...")
    
    # Switch to the newest tab
    driver.switch_to.window(driver.window_handles[-1])
    
    print(f"Switched to tab: {driver.current_url}")
    
    try:
        print("Waiting for section to appear...")
        section = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "section#legend-parts"))
        )
        print("Found the section!")

        # Get the outer HTML of the section
        html_content = section.get_attribute('outerHTML')
        print(f"Retrieved HTML content ({len(html_content)} characters)")
        
        soup = BeautifulSoup(html_content, "html.parser")
        # Find all parts-item divs but exclude those with the "dn" class
        parts_items = soup.find_all('div', class_='parts-item')
        filtered_items = [item for item in parts_items if 'dn' not in item.get('class', [])]

        # Extract the data you want from each item
        parts_data = []
        for item in filtered_items:
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
            
            parts_data.append({
                'order_number': order_number,
                'part_number': part_number,
                'description': description,
                'quantity': quantity
            })

        # Print the extracted data
        for part in parts_data:
            print(f"Order Number: {part['order_number']}")
            print(f"Part Number: {part['part_number']}")
            print(f"Description: {part['description']}")
            print(f"Quantity: {part['quantity']}")
            print("-" * 40)

        # Add to collection with URL and timestamp
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        collected_html_sections.append({
            "url": driver.current_url,
            "timestamp": timestamp,
            "html": html_content
        })

        # Save individual file
        sanitized_timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"section_{sanitized_timestamp}.html"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html_content)

        # Save all sections to one file
        with open("all_sections.html", "w", encoding="utf-8") as f:
            for section_data in collected_html_sections:
                f.write(f"\n<!-- URL: {section_data['url']} -->\n")
                f.write(f"<!-- Timestamp: {section_data['timestamp']} -->\n")
                f.write(section_data['html'])
                f.write("\n\n" + "-"*80 + "\n\n")

        print(f"Saved section HTML to {filename}")
        print(f"Total sections collected: {len(collected_html_sections)}")

    except Exception as e:
        print(f"Error finding section: {e}")
        print("Section with id='legend-parts' not found on this page.")
        traceback.print_exc()

# Debug function to check if the section exists or find alternatives
def debug_page():
    print("\n--- PAGE DEBUG INFO ---")
    print(f"Current URL: {driver.current_url}")
    print(f"Page title: {driver.title}")
    
    try:
        section = driver.find_element(By.CSS_SELECTOR, "section#legend-parts")
        print("Found <section id='legend-parts'>!")
        print(f"Section text preview: {section.text[:100]}...")
    except:
        print("Could NOT find <section id='legend-parts'>")
        sections = driver.find_elements(By.TAG_NAME, "section")
        if sections:
            print(f"Found {len(sections)} other <section> elements:")
            for i, s in enumerate(sections[:5]):
                try:
                    section_id = s.get_attribute('id') or "no-id"
                    section_class = s.get_attribute('class') or "no-class"
                    section_text = s.text[:50] + "..." if len(s.text) > 50 else s.text
                    print(f"  - Section {i+1}: id='{section_id}', class='{section_class}'")
                    print(f"    Text preview: '{section_text}'")
                except:
                    pass
        else:
            print("No <section> elements found on page")
    
    print("\nSuggested next steps:")
    print("1. Use browser developer tools (F12) to verify the correct selector")
    print("2. Check if the section ID might be different")
    print("3. If needed, update the script with the correct selector")
    print("--- END DEBUG INFO ---\n")

# Set up keyboard shortcut listener
def on_press(key):
    try:
        if key.char == 's':
            print("Saving current page section...")
            save_current_page()
        elif key.char == 'd':
            print("Debugging page elements...")
            debug_page()
        elif key.char == 'q':
            print("Saving and quitting...")
            with open("all_sections_final.html", "w", encoding="utf-8") as f:
                for section_data in collected_html_sections:
                    f.write(f"\n<!-- URL: {section_data['url']} -->\n")
                    f.write(f"<!-- Timestamp: {section_data['timestamp']} -->\n")
                    f.write(section_data['html'])
                    f.write("\n\n" + "-"*80 + "\n\n")
            print(f"Saved {len(collected_html_sections)} sections to all_sections_final.html")
            return False  # Stop listener
    except AttributeError:
        pass
    except Exception as e:
        print(f"Error in key handler: {e}")

# Start listener
listener = keyboard.Listener(on_press=on_press)
listener.start()

# Keep script running
try:
    listener.join()
finally:
    driver.quit()

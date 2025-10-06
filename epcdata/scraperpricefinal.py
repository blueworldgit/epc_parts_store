from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from pynput import keyboard
import time
import traceback
import json
from bs4 import BeautifulSoup
import os
from datetime import datetime

# Initialize data storage
collected_html_sections = []
collected_form_data = []

# Set up browser (NOT headless so you can see and interact with it)
options = Options()
options.add_experimental_option("detach", True)  # Keeps browser open
driver = webdriver.Chrome(options=options)

# Navigate to login page
login_url = "https://xt.harrisgroup.ie/welcome"
driver.get(login_url)

# Store the original window handle for reference
original_window = driver.current_window_handle

# Prompt user to manually login
print("Please log in manually in the browser window...")

# Extract form data using JavaScript
def extract_all_form_values():
    try:
        form_data = driver.execute_script(""" 
            const allFormData = {
                timestamp: new Date().toISOString(),
                url: window.location.href,
                title: document.title,
                forms: [],
                allInputs: [],
                selectInputs: [],
                textareaInputs: []
            };

            const forms = document.querySelectorAll('form');
            forms.forEach((form, formIndex) => {
                const formInfo = {
                    formIndex: formIndex,
                    id: form.id,
                    name: form.name,
                    action: form.action,
                    method: form.method,
                    className: form.className,
                    fields: []
                };

                const formControls = form.querySelectorAll('input, select, textarea');
                formControls.forEach((control, controlIndex) => {
                    const fieldInfo = {
                        index: controlIndex,
                        tagName: control.tagName.toLowerCase(),
                        type: control.type || '',
                        name: control.name || '',
                        id: control.id || '',
                        className: control.className || '',
                        value: control.value || '',
                        checked: control.checked || false,
                        selected: control.selected || false,
                        disabled: control.disabled || false,
                        readonly: control.readOnly || false,
                        placeholder: control.placeholder || '',
                        maxLength: control.maxLength || null,
                        title: control.title || '',
                        'aria-label': control.getAttribute('aria-label') || '',
                        'data-tooltip': control.getAttribute('data-tooltip') || ''
                    };

                    if (control.tagName.toLowerCase() === 'select') {
                        fieldInfo.options = Array.from(control.options).map(option => ({
                            value: option.value,
                            text: option.text,
                            selected: option.selected
                        }));
                    }

                    formInfo.fields.push(fieldInfo);
                });

                allFormData.forms.push(formInfo);
            });

            const allInputs = document.querySelectorAll('input');
            allInputs.forEach((input, index) => {
                allFormData.allInputs.push({
                    index: index,
                    tagName: input.tagName.toLowerCase(),
                    type: input.type || '',
                    name: input.name || '',
                    id: input.id || '',
                    className: input.className || '',
                    value: input.value || '',
                    checked: input.checked || false,
                    disabled: input.disabled || false,
                    readonly: input.readOnly || false,
                    placeholder: input.placeholder || '',
                    maxLength: input.maxLength || null,
                    title: input.title || '',
                    'aria-label': input.getAttribute('aria-label') || '',
                    'data-tooltip': input.getAttribute('data-tooltip') || '',
                    outerHTML: input.outerHTML
                });
            });

            const allSelects = document.querySelectorAll('select');
            allSelects.forEach((select, index) => {
                allFormData.selectInputs.push({
                    index: index,
                    name: select.name || '',
                    id: select.id || '',
                    className: select.className || '',
                    value: select.value || '',
                    disabled: select.disabled || false,
                    title: select.title || '',
                    options: Array.from(select.options).map(option => ({
                        value: option.value,
                        text: option.text,
                        selected: option.selected
                    }))
                });
            });

            const allTextareas = document.querySelectorAll('textarea');
            allTextareas.forEach((textarea, index) => {
                allFormData.textareaInputs.push({
                    index: index,
                    name: textarea.name || '',
                    id: textarea.id || '',
                    className: textarea.className || '',
                    value: textarea.value || '',
                    disabled: textarea.disabled || false,
                    readonly: textarea.readOnly || false,
                    placeholder: textarea.placeholder || '',
                    title: textarea.title || ''
                });
            });

            return allFormData;
        """)
        collected_form_data.append(form_data)
        return form_data
    except Exception as e:
        print(f"Error extracting form values: {e}")
        traceback.print_exc()
        return None
    
start = 0 # array position to start (inclusive)
end = 600  # array position to end (exclusive)
# List of codes to process
codes = [
    "B00004107", "B00004764", "B00004858", "B00004859", "B90000877", "B90001169", "C00000601-A133", "C00001726", "C00003208", "C00003209",
    "C00005812", "C00005814", "C00005815", "C00005816", "C00005817", "C00005818", "C00005819", "C00005820", "C00005821", "C00005822",
    "C00005823", "C00005824", "C00005825", "C00005826", "C00005827", "C00005829", "C00005830", "C00005831", "C00005935", "C00013585",
    "C00013586", "C00013593", "C00015967", "C00015968", "C00015981", "C00015982", "C00017192-F001", "C00017616", "C00017617", "C00017618",
    "C00017619", "C00017620", "C00017621", "C00017622", "C00017623", "C00017624", "C00017625", "C00017626", "C00017627", "C00020489",
    "C00022606", "C00023898", "C00024573", "C00026641-F017", "C00027222-4100", "C00027367", "C00027370", "C00032363", "C00037326", "C00042678",
    "C00045073", "C00056425", "C00066424-4100", "C00072270-B", "C00072270-C", "C00072270-D", "C00072270-E", "C00072270-F", "C00072270-G", "C00072843",
    "C00073043", "C00073043", "C00073043", "C00073044", "C00073044", "C00073044", "C00073045", "C00073045", "C00073045", "C00073046",
    "C00073046", "C00073046", "C00073635", "C00074545", "C00074582", "C00074583", "C00075250", "C00075255", "C00075684", "C00075685",
    "C00075686", "C00075687", "C00075688", "C00076123-A007", "C00076336", "C00076863", "C00077218-A133", "C00077223", "C00077242", "C00077262",
    "C00077426", "C00078379-F050", "C00078397-A131", "C00080001", "C00080429", "C00080566", "C00080744", "C00080861-4100", "C00080914-4100", "C00081135-4100",
    "C00083490", "C00084385", "C00084404", "C00084801", "C00084813", "C00084952", "C00085341", "C00085392", "C00085393", "C00085503",
    "C00085566", "C00085567", "C00085651", "C00085902", "C00085913", "C00085967", "C00086253-4100", "C00086286-4100", "C00087356", "C00087585-4100",
    "C00087670-4100", "C00087852", "C00088388", "C00089117-4100", "C00090243", "C00090252-4100", "C00092299", "C00095413", "C00095414", "C00095484",
    "C00095485", "C00097243", "C00097258", "C00097277", "C00097349", "C00097393-4100", "C00097395-4100", "C00097402-4100", "C00097403-4100", "C00097416-4100",
    "C00097417-4100", "C00097422-4100", "C00097464-4100", "C00097465-4100", "C00097467-4100", "C00097474-4100", "C00097475-4100", "C00097689", "C00097750-4100", "C00098037-4100",
    "C00098097-4100", "C00098199-4100", "C00099102-4100", "C00099103-4100", "C00099635-4100", "C00100189-A136", "C00101827-4100", "C00101866", "C00102212", "C00102252",
    "C00102581-4100", "C00103428", "C00103546", "C00103938", "C00103959", "C00104607", "C00105000", "C00105003", "C00105004", "C00105005",
    "C00105102", "C00105336", "C00105340", "C00105979-4100", "C00106878-4100", "C00106879-4100", "C00106909", "C00106920", "C00107801-4100", "C00108334",
    "C00108335", "C00109185-4100", "C00109668", "C00109672", "C00109697", "C00109702", "C00110318", "C00110325", "C00112280-F014", "C00112356-4100",
    "C00112461-4100", "C00113582-4100", "C00113644", "C00117852-4100", "C00117991", "C00117992", "C00118088-2144", "C00118100-F067", "C00118331-4100", "C00118988-4100",
    "C00119242", "C00120457", "C00120499", "C00120500", "C00122574", "C00122579", "C00123939", "C00124370", "C00124921", "C00125039",
    "C00128220", "C00128471", "C00128487", "C00134447-4100", "C00134537", "C00134553", "C00137544", "C00138382", "C00142714", "C00143480",
    "C00143482", "C00144867-A133", "C00145263", "C00145293", "C00146565", "C00146573", "C00147880", "C00153841", "C00154341", "C00154488-4100",
    "C00156174", "C00165566", "C00165650", "C00165784", "C00165851", "C00166539", "C00167481", "C00169136", "C00174126-D128", "C00174384",
    "C00176484", "C00180031", "C00180032", "C00180866", "C00182324-4100", "C00183602", "C00184428", "C00184468", "C00185735", "C00186732",
    "C00191100-F139", "C00191101-F139", "C00191289", "C00191296", "C00191301-4100", "C00191654", "C00191655", "C00193380", "C00193841", "C00195768",
    "C00198477", "C00198480", "C00199382", "C00199837", "C00200268", "C00200270", "C00200521-4100", "C00200878", "C00202003", "C00203234",
    "C00206002", "C00207343", "C00207615", "C00210106", "C00211077", "C00211082", "C00211100", "C00211114", "C00211163", "C00211164",
    "C00211165", "C00211169", "C00211249", "C00211486-A126", "C00212072", "C00212331", "C00213564", "C00213565", "C00213568", "C00213571",
    "C00213573", "C00213574", "C00213575", "C00213576", "C00213577", "C00213578", "C00213579", "C00213581", "C00213582", "C00213583",
    "C00213625", "C00213633", "C00215327", "C00215485", "C00216406", "C00216684", "C00218298", "C00218303", "C00218477", "C00220657",
    "C00220660", "C00220664", "C00221439", "C00224751", "C00229774", "C00235572-4100", "C00235824", "C00235835", "C00236683", "C00237251-4100",
    "C00241088-4100", "C00243060", "C00243346", "C00247000-4100", "C00248518-4100", "C00248838", "C00254221-4100", "C00264290", "C00267531", "C00268263",
    "C00268265", "C00268267", "C00268268", "C00268855", "C00268856", "C00268857", "C00268858", "C00268860", "C00268862", "C00270572",
    "C00274529", "C00275602", "C00275603", "C00276787", "C00277590", "C00278385", "C00279853", "C00280119", "C00280125", "C00280478",
    "C00280656", "C00281639", "C00283252-4100", "C00288607", "C00290803-4100", "C00290804-4100", "C00291597", "C00291598", "C00306666", "C00306700-4100",
    "C00308691-4100", "C00308737", "C00313113", "C00313462", "C00314991", "C00314993", "C00315897", "C00316705", "C00325156", "C00326298",
    "C00333494", "C00333495", "C00334164", "C00334166", "C00336020", "C00339887", "C00341433", "C00342451", "C00348029", "C00349765-A136",
    "C00352818", "C00352821", "C00384599", "C00392360", "C00393228-4100", "C00399477", "C00399478", "C00419031", "C00419032", "C00423609",
    "C00427675", "C00428094", "C00429557", "C00430210", "C00446282", "C00452602", "C00452603", "C00457818", "C00457823", "C00469711",
    "C00471078", "C00471087", "C00472602", "C00473445", "C00476279", "C00489232", "C00489676", "C00489677", "C00494020", "C00521629",
    "C00532115", "C00539863", "C00539866", "C00539867", "C00543551", "C00543551", "C00543551", "C00559196", "C00559199", "C00559202",
    "C00559204", "C00559206", "C00564032", "C00564033", "C00564035", "C00564042", "C00570065", "C00585980", "C00587973", "C00618313",
    "C00618314", "C00637484", "C00638474", "C00638478", "C00638479", "C00638735", "C00638736", "C00642739", "C00649758", "C00671897",
    "C00671899", "C00678886", "C00678889", "C00679772", "C00690364", "C00693370", "C00697790", "C00697791", "C00704930", "C00704931",
    "C00704932", "C00729579", "C00731552", "C00744243", "C00752821", "C00888852", "C00888881", "C00888882"
]

def extract_whs_and_stock():
    try:
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        # Find the exact match for the target row div
        target_div = soup.find("div", style=lambda s: s and
            "overflow: hidden" in s and
            "user-select: none" in s and
            "height: 19px" in s and
            "position: relative" in s and
            "z-index: 0" in s and
            "width: 1072px" in s and
            "border-bottom-color: transparent" in s)

        if not target_div:
            print("❌ Specific styled target row div not found.")
            return {}

        # Now find first two z-index: 3 divs inside
        z3_divs = target_div.find_all("div", style=lambda s: s and "z-index: 3" in s)
        if len(z3_divs) < 2:
            print("❌ Less than two z-index:3 divs found.")
            return {}

        whs_value = z3_divs[0].get_text(strip=True)
        stock_value = z3_divs[1].get_text(strip=True)

        return {
            "whs": whs_value,
            "stock_available": stock_value
        }

    except Exception as e:
        print(f"Error extracting WHS and stock: {e}")
        traceback.print_exc()
        return {}

# Create output folder named with date and time
output_folder = datetime.now().strftime("output_%Y%m%d_%H%M%S")
os.makedirs(output_folder, exist_ok=True)

# Create non-matches filename with date
nonmatches_filename = datetime.now().strftime("nonmatches_%Y%m%d_%H%M%S.txt")

def verify_correct_code_displayed(expected_code):
    """Verify that the correct code is displayed in the input field after submission"""
    try:
        # Check the active input element
        active_element = driver.switch_to.active_element
        current_value = active_element.get_attribute('value')
        
        if current_value == expected_code:
            return True, current_value
        else:
            print(f"⚠️  CODE MISMATCH: Expected '{expected_code}', but found '{current_value}'")
            return False, current_value
            
    except Exception as e:
        print(f"Error verifying code: {e}")
        return False, "ERROR"

def run_all_codes():
    print("Finding XT window...")

    xt_window = None
    all_windows = driver.window_handles

    for window_handle in all_windows:
        driver.switch_to.window(window_handle)
        if "XT" in driver.title:
            xt_window = window_handle
            print(f"Found XT window: {driver.title}")
            break

    if not xt_window:
        print("XT window not found.")
        return

    driver.switch_to.window(xt_window)

    # Adjust end if it's out of range
    actual_end = end if end <= len(codes) else len(codes)
    selected_codes = codes[start:actual_end]
    
    # Track statistics
    successful_codes = []
    mismatched_codes = []
    error_codes = []
    
    for code in selected_codes:
        try:
            print(f"\nProcessing code: {code}")
            active_element = driver.switch_to.active_element
            active_element.clear()
            active_element.send_keys(code)
            active_element.send_keys(Keys.RETURN)

            print("Submitted. Waiting for response...")
            time.sleep(2)

            # Verify the correct code is displayed
            is_correct, displayed_code = verify_correct_code_displayed(code)
            
            if is_correct:
                print(f"✅ Code verified: {displayed_code}")
                
                form_data = extract_all_form_values()
                extra_data = extract_whs_and_stock()

                if form_data:
                    form_data['whs_stock'] = extra_data
                    form_data['verified_code'] = displayed_code
                    form_data['original_search_code'] = code
                    
                    filename = os.path.join(output_folder, f"{code}.json")
                    with open(filename, "w", encoding="utf-8") as f:
                        json.dump(form_data, f, indent=2, ensure_ascii=False)
                    print(f"✅ Saved verified data to {filename}")
                    successful_codes.append(code)
                else:
                    print(f"❌ No form data extracted for {code}")
                    error_codes.append(code)
            else:
                print(f"❌ SKIPPING: Code mismatch for {code} (got {displayed_code})")
                mismatched_codes.append({'searched': code, 'found': displayed_code})
                
                # Save mismatch info for reference
                mismatch_data = {
                    'original_search_code': code,
                    'displayed_code': displayed_code,
                    'status': 'CODE_MISMATCH',
                    'timestamp': datetime.now().isoformat()
                }
                filename = os.path.join(output_folder, f"{code}_MISMATCH.json")
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(mismatch_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"❌ Error with code {code}: {e}")
            error_codes.append(code)
            traceback.print_exc()
    
    # Save non-matches to dated file
    if mismatched_codes:
        nonmatches_path = os.path.join(output_folder, nonmatches_filename)
        with open(nonmatches_path, "w", encoding="utf-8") as f:
            f.write(f"NON-MATCHING CODES REPORT\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total non-matches: {len(mismatched_codes)}\n")
            f.write(f"{'='*60}\n\n")
            
            for i, mismatch in enumerate(mismatched_codes, 1):
                f.write(f"{i:3d}. Searched: {mismatch['searched']:<15} → Found: {mismatch['found']}\n")
            
            f.write(f"\n{'='*60}\n")
            f.write(f"Summary: {len(mismatched_codes)} codes did not match exactly\n")
            f.write(f"These codes may need manual review or correction\n")
        
        print(f"💾 Non-matches saved to: {nonmatches_path}")
    
    # Print summary
    print(f"\n📊 PROCESSING SUMMARY:")
    print(f"   ✅ Successful: {len(successful_codes)}")
    print(f"   ⚠️  Code mismatches: {len(mismatched_codes)}")
    print(f"   ❌ Errors: {len(error_codes)}")
    
    if mismatched_codes:
        print(f"\n⚠️  MISMATCHED CODES (first 5):")
        for mismatch in mismatched_codes[:5]:  # Show first 5
            print(f"   {mismatch['searched']} → {mismatch['found']}")
        if len(mismatched_codes) > 5:
            print(f"   ... and {len(mismatched_codes) - 5} more (see {nonmatches_filename})")
    
    print("✅ Finished processing selected codes.")

# Keyboard event handlers
def on_press(key):
    try:
        if hasattr(key, 'char') and key.char:
            if key.char.lower() == 'g':
                run_all_codes()
            elif key.char.lower() == 'q':
                print("\nQuitting and saving collected form data if any...")
                if collected_form_data:
                    with open("collected_form_data.json", "w", encoding="utf-8") as f:
                        json.dump(collected_form_data, f, indent=2, ensure_ascii=False)
                    print("Form data saved to 'collected_form_data.json'")
                driver.quit()
                return False
        elif key == keyboard.Key.enter:
            print("Enter key pressed (no action assigned).")
    except AttributeError:
        pass

input("Press Enter once you've logged in successfully...")

print("\n✅ Ready!")
print("→ Press 'g' to process all codes.")
print("→ Press 'q' to quit and save.")
print("Listening for keystrokes...")

with keyboard.Listener(on_press=on_press) as listener:
    listener.join()

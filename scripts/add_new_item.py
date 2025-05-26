import os
import time
import random
from collections import defaultdict
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from functools import wraps

from helper.browser_manager import create_driver
from helper.common_utils import load_credentials, log
from helper.fronocloud_login import login

from google.oauth2 import service_account
from googleapiclient.discovery import build



# Configuration Constants
SIZE_MAPPING = {
    '36': 'S',
    '38': 'M',
    '40': 'L',
    '42': 'XL',
    '44': 'XXL',
    '46': 'XXXL'
}

SIZE_SETS = {
    '38-44': [38, 40, 42, 44], 
    '40-46': [40, 42, 44, 46], 
    '48-52': [48, 50, 52]
}

ALL_SIZES = [36, 38, 40, 42, 44, 46, 48, 50, 52, 60]

# Default values for dropdowns
DROPDOWN_OPTIONS = {
    'unit': ' Pieces',
    'glaccount': ' Purchase',
    'category': ' Finish goods',
    'subcategory': ' Kurti',
    'brand': 'OLIVIA ',
    'group': ' PK'
}

# Timeouts and delays
DEFAULT_TIMEOUT = 10
DEFAULT_DELAY = 1
MAX_RETRIES = 3

def get_google_credentials():
    """
    Get Google credentials from environment or service account file.
    Returns service account credentials for Google Sheets API.
    """
    if not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        if os.path.exists("service_account_key.json"):
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "service_account_key.json"
            log("✅ Set GOOGLE_APPLICATION_CREDENTIALS for local run.")
        else:
            raise EnvironmentError("No Google credentials found. Please set GOOGLE_APPLICATION_CREDENTIALS or provide service_account_key.json")

    return service_account.Credentials.from_service_account_file(
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"],
        scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
    )

def generate_sample_items():
    """
    Generate sample items data for testing or fallback purposes.
    Returns a list of sample items with random colors and sizes.
    """
    size_mapping = {
        '36': 'S',
        '38': 'M',
        '40': 'L',
        '42': 'XL',
        '44': 'XXL',
        '46': 'XXXL'
    }
    available_sizes = list(size_mapping.keys())
    available_colors = ['RED', 'BLUE', 'GREEN', 'BLACK', 'WHITE', 'YELLOW', 'PURPLE', 'PINK']
    
    sample_items = [
        {
            'Design No.': f'TI{i:03d}',
            'Unit': 'PCS',
            'HSN Code': f'1234{i:02d}',
            'Colors': random.sample(available_colors, k=random.randint(2, len(available_colors))),
            'Sizes': random.sample(available_sizes, k=random.randint(2, len(available_sizes))),
        }
        for i in range(1, 6)
    ]
    return sample_items

def fetch_items_from_sheet():
    """
    Fetch items data from a Google Sheet.
    The sheet should have columns: Design No., Unit, HSN Code, Colors, Sizes
    Colors and Sizes should be comma-separated values in their respective cells.
    """
    try:
        # Get credentials and build service
        credentials = get_google_credentials()
        service = build('sheets', 'v4', credentials=credentials)

        # The ID of the spreadsheet to retrieve data from
        SPREADSHEET_ID = os.environ.get('ITEMS_SPREADSHEET_ID')
        if not SPREADSHEET_ID:
            raise EnvironmentError("ITEMS_SPREADSHEET_ID environment variable not set")

        # The range of the sheet to retrieve data from (e.g., 'Sheet1!A2:E')
        RANGE_NAME = 'Sheet1!A2:C'  # Assuming headers are in row 1
        
        # Call the Sheets API
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME
        ).execute()

        values = result.get('values', [])
        if not values:
            log("No data found in the spreadsheet.")
            return []

        # Process the data
        items = []
        for row in values:
            if len(row) > 2:  # Ensure we have all required columns
                item = {
                    'Design No.': row[0],
                    'Unit': 'PCS',
                    'HSN Code': '123456',
                    'Colors': [color.strip() for color in row[1].split(',')],
                    'Sizes': [size.strip() for size in row[2].split(',')]
                }
                items.append(item)

        log(f"Successfully fetched {len(items)} items from Google Sheet")
        return items

    except Exception as e:
        log(f"Error fetching items from Google Sheet: {e}")
        log("Using sample data as fallback")
        return generate_sample_items()

def merge_items(raw_items):
    merged = defaultdict(lambda: {
        'Unit': 'PCS',
        'HSN Code': '123456',
        'Colors': set(),
        'Sizes': set()
    })

    for item in raw_items:
        design = item['Design No.']
        merged[design]['Colors'].update(item.get('Colors', [])) # type: ignore
        merged[design]['Sizes'].update(item.get('Sizes', [])) # type: ignore

    # Convert sets to sorted lists and build final list
    final_items = []
    for design, data in merged.items():
        final_items.append({
            'Design No.': design,
            'Unit': data['Unit'],
            'HSN Code': data['HSN Code'],
            'Colors': sorted(data['Colors']),
            'Sizes': sorted(data['Sizes'])
        })

    return final_items

def design_exists(driver, design_no):
    try:
        # Clear and enter the design number in the search field
        search_input = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, '//input[@id="globalSearch"]'))
        )
        search_input.clear()
        search_input.send_keys(design_no)
        search_input.send_keys(Keys.ENTER)

        time.sleep(2)  # Small delay for search results to load

        # Check if the design number appears in the first row
        result_xpath = f"//*[@id='pn_id_3-table']/tbody/tr/td/div[contains(text(), '{design_no}')]"
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, result_xpath))
        )
        return True
    except:
        return False


def retry_on_failure(max_attempts=3, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except (TimeoutException, StaleElementReferenceException) as e:
                    attempts += 1
                    if attempts == max_attempts:
                        raise e
                    time.sleep(delay)
            return None
        return wrapper
    return decorator

@retry_on_failure(max_attempts=3)
def wait_and_click(driver, xpath, timeout=10):
    element = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.XPATH, xpath))
    )
    element.click()
    return element

@retry_on_failure(max_attempts=3)
def wait_and_send_keys(driver, xpath, keys, timeout=10):
    element = WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.XPATH, xpath))
    )
    element.clear()
    element.send_keys(keys)
    return element


def addNewItem(location):
    username, password = load_credentials(location)
    driver = create_driver()
    actions = ActionChains(driver)
    failed_items = []
    success_count = 0

    try:
        # Fetch items to add
        items_to_add = merge_items(fetch_items_from_sheet())

        if not items_to_add:
            log("No new items to add")
            return "No items to add"

        log(f"Starting to process {len(items_to_add)} items...")
        login(driver, username, password)

        log("Navigating to Items page...")
        time.sleep(DEFAULT_DELAY)
        driver.get(driver.current_url.replace("/dashboard", "/item/view"))

        # Filter out items that already exist
        unique_items = []
        for item in items_to_add:
            design_no = item['Design No.']
            if design_exists(driver, design_no):
                log(f"🟡 Skipping existing design: {design_no}")
            else:
                unique_items.append(item)

        if not unique_items:
            log("✅ All items already exist. Nothing to add.")
            return "All items already exist."
        
# ========================= Fix: Also modify the existing items if there is a change in any value ========================= #

        # Update items_to_add to only include unique items
        wait_and_click(driver, "//button[contains(text(), ' Add New Item ')]")

        # Process each item
        for item in unique_items:
            try:
                log(f"Processing item: {item['Design No.']}")
                
                if not item.get('Sizes'):
                    log(f"⚠️ No size sets provided for item {item['Design No.']}, skipping...")
                    failed_items.append(item['Design No.'])
                    continue
                
                time.sleep(DEFAULT_DELAY)
                
                # Fill in product details using retry mechanism
                wait_and_send_keys(driver, '//input[@id="productname"]', item['Design No.'])
                wait_and_send_keys(driver, '//input[@id="productcode"]', item['Design No.'])
                
                # Select dropdowns using configuration
                for field, value in DROPDOWN_OPTIONS.items():
                    try:
                        wait_and_click(driver, f"//select[@id='{field}']/option[text()='{value}']")
                    except Exception as e:
                        log(f"Warning: Could not select {field}: {e}")
                        raise

                # Handle Colors
                wait_and_click(driver, "//button[contains(text(), 'Select Color')]")
                wait_and_click(driver, "//label[contains(text(), ' All Colors ')]")

                # Select each color from the item's colors list
                for color in item['Colors']:
                    print(f"Processing color: {color}")
                    try:
                        # Try clicking the color from the table
                        color_label = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, f"//td[contains(text(), '{color.upper()}')]"))
                        )
                        color_label.find_element(By.XPATH, "./preceding-sibling::td").click()
                   
                    except Exception as e:
                        log(f"Warning: Could not select color {color}: {e.__class__.__name__} - {str(e)}")

                        try:
                            # Step 1: Fill in the color manually
                            color_input = WebDriverWait(driver, 5).until(
                                EC.presence_of_element_located((By.ID, 'colorname'))
                            )
                            color_input.clear()
                            color_input.send_keys(color)

                            code_input = WebDriverWait(driver, 5).until(
                                EC.presence_of_element_located((By.ID, 'colorcode'))
                            )
                            code_input.clear()
                            code_input.send_keys(color)

                            # Step 2: Move focus and trigger click
                            actions.send_keys(Keys.TAB).perform()

                            # Try clicking directly
                            elem = driver.switch_to.active_element
                            elem.click()

                            # Step 3: Wait for the new color to appear in the list and select it
                            color_label = WebDriverWait(driver, 10).until(
                                EC.element_to_be_clickable((By.XPATH, f"//td[normalize-space(text())='{color.upper()}']"))
                            )
                            color_label.find_element(By.XPATH, "./preceding-sibling::td").click()

                        except Exception as inner_e:
                            log(f"Manual entry + select failed for color {color}: {inner_e}")

                # Confirm selection
                wait_and_click(driver, "//button[contains(text(), 'OK')]")
                
                # Handle Sizes
                wait_and_click(driver, "//select[@id='sizeGrp']/option[2]")
                wait_and_click(driver, "//button/span[contains(text(), 'Size Set')]")

                # Select each size from the item's sizes list
                for size in item['Sizes']:
                    try:
                        size_set_label = wait_and_click(driver, f"//td[contains(text(), '{size}')]")
                        size_set_label.find_element(By.XPATH, "./preceding-sibling::td").click()
                    except Exception as e:
                        log(f"Warning: Could not select size {size}: {e}")
                        raise

                # Add selected sizes
                wait_and_click(driver, "//button[contains(text(), 'Add')]")
                
                # Handle checkboxes
                targets = set(s for r in item['Sizes'] for s in SIZE_SETS[r])
                actions.send_keys(Keys.TAB * 2)

                for i, size in enumerate(ALL_SIZES):
                    if size in targets:
                        actions.send_keys(Keys.SPACE)
                    if i < len(ALL_SIZES) - 1:
                        actions.send_keys(Keys.TAB)

                actions.perform()
                time.sleep(DEFAULT_DELAY * 1)

                # Save the item
                wait_and_click(driver, "//button[contains(text(), ' Add')]")

                # Wait for success message or error
                try:
                    WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, "//div[@role='alert' and @aria-label='Successfully added']"))
                    )
                    log(f"✅ Successfully added item: {item['Design No.']}")
                    success_count += 1
                except:
                    log(f"⚠️ Item {item['Design No.']} may not have been added successfully / already present")
                    failed_items.append(item['Design No.'])


            except Exception as e:
                log(f"❌ Error processing item {item['Design No.']}: {e}")
                failed_items.append(item['Design No.'])
                continue
            
            driver.refresh()

        summary = f"Processed {len(items_to_add)} items: {success_count} successful, {len(failed_items)} failed"
        if failed_items:
            summary += f"\nFailed items: {', '.join(failed_items)}"
        print(summary)

    except Exception as e:
        log(f"❌ Error during item addition process: {e}")
        return f"Error: {e}"

    finally:
        log("Closing browser...")
        driver.quit()

addNewItem("kolkata")
import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from scripts.helper.browser_manager import create_driver
from scripts.helper.common_utils import ensure_download_path, load_credentials, log, upload_to_bigquery, wait_for_download
from scripts.helper.fronocloud_login import login

def getPurchasePendingOrder():
    folder = "Frono_Purchase_Pending_Order_Report"
    download_path = ensure_download_path(folder)
    username, password = load_credentials()
    driver = create_driver(download_path)
    actions = ActionChains(driver)

    try:
        log("Opening FronoCloud login page and logging in...")
        login(driver, username, password)

        log("Navigating to 'Pending Purchase Order' report...")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "pn_id_3_7_header"))).click()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.LINK_TEXT, "Pending Purchase Order"))).click()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="vendorWise-tab-justified"]'))).click()

        time.sleep(2)
        btn = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//button[@id="08"]')))
        driver.execute_script("arguments[0].focus();", btn)

        time.sleep(1)
        actions.send_keys(Keys.TAB * 3).perform()
        driver.execute_script("arguments[0].click();", driver.switch_to.active_element)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[text()='This Financial Year']"))).click()

        driver.execute_script("arguments[0].focus();", btn)
        actions.key_down(Keys.SHIFT).send_keys(Keys.TAB).key_up(Keys.SHIFT).send_keys(Keys.SPACE).perform()
        time.sleep(1)
        actions.key_down(Keys.SHIFT).send_keys(Keys.TAB).key_up(Keys.SHIFT).send_keys(Keys.SPACE).perform()
        actions.send_keys(Keys.ESCAPE).perform()

        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[text()=' Search ']"))).click()
        time.sleep(10)

        log("Exporting to Excel...")
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//*[@title='Excel']"))).click()
        
        downloaded_file = wait_for_download(download_path)
        log(f"✅ Downloaded file saved as: {downloaded_file}")

        # Upload to BigQuery
        upload_to_bigquery(downloaded_file, table_name="purchase_pending")

        # Delete file
        os.remove(downloaded_file)
        log(f"🗑️ Deleted local file: {downloaded_file}")

        return f"Success: {downloaded_file}"

    except Exception as e:
        log(f"❌ Error during scraping: {e}")
        return f"Error: {e}"

    finally:
        log("Closing browser...")
        driver.quit()


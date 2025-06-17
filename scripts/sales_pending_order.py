import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from scripts.df_cleaners.cleaner import modify_order_dataframe
from scripts.helper.browser_manager import create_driver
from scripts.helper.common_utils import ensure_download_path, load_credentials, load_dataframe, log, upload_to_bigquery, wait_for_download
from scripts.helper.fronocloud_login import login


def getSalesPendingOrderThis(location):
    folder = "Frono_Sales_Pending_Order_Report"
    download_path = ensure_download_path(location, folder)
    username, password = load_credentials(location)
    driver = create_driver(download_path)
    actions = ActionChains(driver)

    try:
        # log("Opening FronoCloud login page and logging in...")
        login(driver, username, password)

        log("Navigating to 'Customer Wise Item Details (Sales Pending Order)' report...")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "pn_id_3_7_header"))).click()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.LINK_TEXT, "Customer Wise Item Details"))).click()
        time.sleep(1)

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//button[@title='Advance filter']"))).click()
        time.sleep(2)
        actions.key_down(Keys.ALT).send_keys('a').key_up(Keys.ALT).perform()
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Apply']"))).click()

        time.sleep(2)
        actions.send_keys(Keys.TAB * 3).perform()
        driver.execute_script("arguments[0].click();", driver.switch_to.active_element)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[text()='This Financial Year']"))).click()

        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[text()=' Search ']"))).click()
        time.sleep(10)

        # log("Exporting to Excel...")
        actions.send_keys(Keys.TAB * 8 + Keys.SPACE).perform()

        downloaded_file = wait_for_download(download_path)
        log(f"✅ Downloaded file saved as: {downloaded_file}")

        df = load_dataframe(downloaded_file)

        df = modify_order_dataframe(df)

        custom_schema = {
            "SO_Date": "DATE",
        }

        # Upload to BigQuery
        upload_to_bigquery(df, table_name="sales_pending", location=location, custom_schema_map=custom_schema)

        # # Delete file
        os.remove(downloaded_file)
        log(f"🗑️ Deleted local file: {downloaded_file}")

        return f"Success"

    except Exception as e:
        log(f"❌ Error during scraping: {e}")
        return f"Error: {e}"

    finally:
        log("Closing browser...")
        driver.quit()

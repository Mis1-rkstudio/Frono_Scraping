import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from scripts.df_cleaners.cleaner import modify_valuation_dataframe
from scripts.helper.browser_manager import create_driver
from scripts.helper.common_utils import ensure_download_path, load_credentials, load_dataframe, log, upload_to_bigquery, wait_for_download
from scripts.helper.fronocloud_login import login

def getStockValuation():
    folder = "Frono_Stock_Valuation_Report"
    download_path = ensure_download_path(folder)
    username, password = load_credentials()
    driver = create_driver(download_path)
    actions = ActionChains(driver)

    try:
        log("Opening FronoCloud login page and logging in...")
        login(driver, username, password)

        log("Navigating to 'Stock Valuation' report...")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "pn_id_3_7_header"))).click()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.LINK_TEXT, "Stock Valuation"))).click()
        time.sleep(1)

        Select(WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "basicSelect")))).select_by_index(0)
        actions.key_down(Keys.SHIFT).send_keys(Keys.TAB * 3 + Keys.ARROW_RIGHT).key_up(Keys.SHIFT).perform()

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//button[@title='Advance filter']"))).click()
        time.sleep(2)
        actions.key_down(Keys.ALT).send_keys('a').key_up(Keys.ALT).perform()
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Apply']"))).click()

        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[text()=' Search ']"))).click()
        time.sleep(10)

        log("Exporting to Excel...")
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//*[@title='Excel']"))).click()

        downloaded_file = wait_for_download(download_path)
        log(f"✅ Downloaded file saved as: {downloaded_file}")

        df = load_dataframe(downloaded_file)

        log("Modifying DataFrame...")
        df = modify_valuation_dataframe(df)

        # Upload to BigQuery
        upload_to_bigquery(downloaded_file, table_name="stock_valuation")

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
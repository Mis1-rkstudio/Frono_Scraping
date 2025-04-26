import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from scripts.df_cleaners.cleaner import modify_stock_dataframe
from scripts.helper.browser_manager import create_driver
from scripts.helper.common_utils import ensure_download_path, load_credentials, load_dataframe, log, upload_to_bigquery, wait_for_download
from scripts.helper.fronocloud_login import login

def getStock():
    folder = "Frono_Stock_Report"
    download_path = ensure_download_path(folder)
    username, password = load_credentials()
    driver = create_driver(download_path)
    actions = ActionChains(driver)

    try:
        log("Logging in to FronoCloud...")
        login(driver, username, password)

        log("Navigating to Stock...")
        time.sleep(2)
        element = driver.find_element(By.CSS_SELECTOR, 'a[title="Stock"][href*="/stock"]')
        driver.execute_script("arguments[0].click();", element)

        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[normalize-space(text())='Stock Summary']"))).click()
        advance_filter_btn = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, '08')))
        driver.execute_script("arguments[0].focus();", advance_filter_btn)
        actions.key_down(Keys.SHIFT).send_keys(Keys.TAB).send_keys(Keys.TAB).send_keys(Keys.ARROW_RIGHT).key_up(Keys.SHIFT).perform()
        advance_filter_btn = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, '08'))).click()
        time.sleep(2)
        actions.key_down(Keys.ALT).send_keys('a').key_up(Keys.ALT).perform()
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Apply']"))).click()
        clear_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[text()=' Clear ']")))
        driver.execute_script("arguments[0].focus();", clear_button)
        actions.key_down(Keys.SHIFT).send_keys(Keys.TAB).send_keys(Keys.TAB).key_up(Keys.SHIFT).perform()
        driver.execute_script("arguments[0].click();", driver.switch_to.active_element)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[text()='Till Date']"))).click()
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[text()=' Search ']"))).click()
        time.sleep(15)

        log("Exporting to Excel...")
        actions.send_keys(Keys.TAB * 11 + Keys.SPACE).perform()
        time.sleep(2)

        downloaded_file = wait_for_download(download_path)
        log(f"✅ Downloaded file saved as: {downloaded_file}")

        df = load_dataframe(downloaded_file)

        log("Modifying DataFrame...")
        df = modify_stock_dataframe(df)

        # Upload to BigQuery
        upload_to_bigquery(df, dataset_id="frono", table_name="stock")

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

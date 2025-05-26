import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from df_cleaners.cleaner import modify_sales_invoice_dataframe
from helper.browser_manager import create_driver
from helper.common_utils import ensure_download_path, load_credentials, load_dataframe, log, upload_to_bigquery, wait_for_download
from helper.fronocloud_login import login


def getSalesInvoice(location):
    folder = "Frono_Sales_Invoice_Report"
    download_path = ensure_download_path(location, folder)
    username, password = load_credentials(location)
    driver = create_driver(download_path)
    actions = ActionChains(driver)

    try:
        # log("Logging in to FronoCloud...")
        login(driver, username, password)

        log("Navigating to Invoice page...")
        time.sleep(2)
        element = driver.find_element(By.CSS_SELECTOR, 'a[title="Invoice"][href*="/purchase/view"]')
        driver.execute_script("arguments[0].click();", element)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "globalSearch"))).click()
        actions.send_keys(Keys.TAB).perform()
        driver.execute_script("arguments[0].click();", driver.switch_to.active_element)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[text()='This Financial Year']"))).click()
        time.sleep(2)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "globalSearch"))).click()
        actions.send_keys(Keys.TAB * 9 + Keys.SPACE).perform()
        time.sleep(2)

        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//*[@title='Excel']"))).click()
        time.sleep(2)

        downloaded_file = wait_for_download(download_path)
        log(f"✅ Downloaded file saved as: {downloaded_file}")

        df = load_dataframe(downloaded_file)

        df = modify_sales_invoice_dataframe(df)

        # Upload to BigQuery
        upload_to_bigquery(df, table_name="sales_invoice", location=location)

        # Delete file
        os.remove(downloaded_file)
        log(f"🗑️ Deleted local file: {downloaded_file}")

        return f"Success"

    except Exception as e:
        log(f"❌ Error during scraping: {e}")
        return f"Error: {e}"

    finally:
        log("Closing browser...")
        driver.quit()

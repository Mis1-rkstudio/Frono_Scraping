import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from scripts.df_cleaners.cleaner import modify_account_payable_dataframe
from scripts.helper.browser_manager import create_driver
from scripts.helper.common_utils import ensure_download_path, load_credentials, load_dataframe, log, upload_to_bigquery, wait_for_download
from scripts.helper.fronocloud_login import login





def getAccountPayable():
    folder = "Frono_Account_Payable_Report"
    download_path = ensure_download_path(folder)
    username, password = load_credentials()
    driver = create_driver(download_path)
    actions = ActionChains(driver)

    try:
        log("Opening FronoCloud login page and logging in...")
        login(driver, username, password)

        log("Navigating to 'Account Payable' report...")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "pn_id_3_7_header"))).click()
        time.sleep(1)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.LINK_TEXT, "Account Payable / Vendor Wise"))).click()
        time.sleep(1)
        
        actions.send_keys(Keys.TAB * 2).perform()
        time.sleep(1)
        actions.send_keys(Keys.SPACE).perform()
        time.sleep(1)
        actions.key_down(Keys.SHIFT).send_keys(Keys.TAB).key_up(Keys.SHIFT).perform()
        time.sleep(1)
        actions.send_keys(Keys.SPACE).perform()
        time.sleep(1)
        actions.send_keys(Keys.ESCAPE).perform()
        time.sleep(1)
        actions.send_keys(Keys.TAB).perform()
        time.sleep(1)

        driver.execute_script("arguments[0].click();", driver.switch_to.active_element)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[text()='This Financial Year']"))).click()

        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[text()=' Search ']"))).click()
        time.sleep(20)
        
        log("Exporting to Excel...")
        actions.send_keys(Keys.TAB * 6 + Keys.SPACE).perform()
        time.sleep(2)

        downloaded_file = wait_for_download(download_path)
        log(f"✅ Downloaded file saved as: {downloaded_file}")

        df = load_dataframe(downloaded_file)

        log("Modifying DataFrame...")
        df = modify_account_payable_dataframe(df)

        # Upload to BigQuery
        upload_to_bigquery(df, table_name="account_payable")

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

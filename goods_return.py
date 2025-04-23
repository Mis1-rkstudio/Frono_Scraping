import os
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

def log(msg):
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)

def wait_for_download(directory, extension=".xlsx", timeout=30):
    log("Waiting for download to complete...")
    end_time = time.time() + timeout
    while time.time() < end_time:
        files = [f for f in os.listdir(directory) if f.endswith(extension) and not f.endswith(".crdownload")]
        if files:
            return os.path.join(directory, files[0])
        time.sleep(1)
    raise Exception("Download timeout")

# Load environment variables
load_dotenv()

def getGoodsReturn():
    download_path = os.path.join(os.getcwd(), "Kolkata", "Frono_Goods_Return_Report")
    os.makedirs(download_path, exist_ok=True)

    FRONO_USERNAME = os.getenv("FRONO_USERNAME")
    FRONO_PASSWORD = os.getenv("FRONO_PASSWORD")

    if not FRONO_USERNAME or not FRONO_PASSWORD:
        raise EnvironmentError("FRONO_USERNAME or FRONO_PASSWORD missing.")

    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")
    # options.add_argument("--no-sandbox")
    # options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"--window-size=1920,1080")
    # options.add_argument(f"--disable-gpu")
    # options.add_argument(f"--disable-software-rasterizer")
    # options.add_argument(f"--remote-debugging-port=9222")
    prefs = {
        "download.default_directory": download_path,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(options=options)
    actions = ActionChains(driver)

    try:
        log("Opening FronoCloud login page...")
        driver.get("https://fronocloud.com/login")

        log("Logging in...")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "userName"))).send_keys(FRONO_USERNAME)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "password"))).send_keys(FRONO_PASSWORD + Keys.RETURN)

        log("Navigating to 'Reports' page...")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "pn_id_3_7_header"))).click()
        log("Navigating to 'Sales Returns'...")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.LINK_TEXT, "GR Customer and Item Wise"))).click()
        time.sleep(2)

        # TODO: Fix the date range selection -----------------------------
        input_elem = driver.find_element(By.NAME, "tlDateType")
        driver.execute_script("arguments[0].click();", input_elem)






        # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@id='button-container1 dropdown-toggle']/input"))).click()
        time.sleep(5)
        
        # log("Opening advanced filter...")
        # WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "09"))).click()
        # time.sleep(1)
        # actions.key_down(Keys.ALT).send_keys('a').key_up(Keys.ALT).perform()
        # WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Apply']"))).click()
        # WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[text()=' Search ']"))).click()
        # log("Exporting to Excel...")
        # WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//*[@title='Excel']"))).click()
        # log("After 'Sales Returns'...")


        # downloaded_file = wait_for_download(download_path)
        # log(f"✅ Downloaded file saved as: {downloaded_file}")
        
    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        driver.quit()

getGoodsReturn()
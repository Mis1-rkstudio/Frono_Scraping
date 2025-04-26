from selenium import webdriver
from selenium.webdriver.chrome.service import Service

def create_driver(download_path):
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--headless")

    # options.binary_location = "/usr/bin/chromium"

    prefs = {
        "download.default_directory": download_path,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    options.add_experimental_option("prefs", prefs)

    # Use Service object to pass chromedriver path
    # service = Service("/usr/bin/chromedriver")
    # return webdriver.Chrome(service=service, options=options)
    return webdriver.Chrome(options=options)

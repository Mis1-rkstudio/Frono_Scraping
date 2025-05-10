from selenium import webdriver
import os


def create_driver(download_path=None):
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless=new")  
    options.add_argument("--window-size=1920,1080")

    # 💡 These 3 suppress common errors in headless/cloud environments
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--disable-features=VizDisplayCompositor")

    # 🛡️ Required for Docker or Cloud Run
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    if download_path:
        os.makedirs(download_path, exist_ok=True)

        # Set up download preferences
        prefs = {
            "download.default_directory": os.path.abspath(download_path),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }

        options.add_experimental_option("prefs", prefs)

    return webdriver.Chrome(options=options)

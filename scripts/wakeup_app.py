import time
import logging

from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

logging.basicConfig(
    level="INFO",
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%d/%m/%Y %H:%M:%S",
    force=True,
)

# Creating webdriver browser
opts = ChromeOptions()
opts.add_argument("--headless")
opts.add_argument("--no-sandbox")
opts.add_argument("--disable-dev-shm-usage")

browser = Chrome(options=opts, keep_alive=True)
browser.implicitly_wait(0.5)
logging.info("Created webdriver browser")

# Open page
browser.get("https://poulpe-padel-tracker.streamlit.app/")
logging.info("Opened streamlit app page successfully")
time.sleep(10)

# Check if inactive
try:
    wakeup_button = browser.find_element(
        By.XPATH, "//*[contains(text(), 'Yes, get this app back up!')]"
    )
except NoSuchElementException:
    logging.info("App is awaken, all OK !")
    browser.quit()
    exit(0)
else:
    logging.warning("App is inactive, awakening in progress (clicked button)")
    wakeup_button.click()
    time.sleep(30)
    try:
        wakeup_button = browser.find_element(
            By.XPATH, "//*[contains(text(), 'Yes, get this app back up!')]"
        )
    except NoSuchElementException:
        logging.info("App is now awaken, all OK !")
        browser.quit()
        exit(0)
    except Exception as exc:
        logging.error(
            f"Visited inactive app page but got unexpected error while awakening: {exc}"
        )
        browser.quit()
        exit(2)
    else:
        logging.error(
            "Visited inactive app page but was unable to awaken, check page manually"
        )
        browser.quit()
        exit(1)

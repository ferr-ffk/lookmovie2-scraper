from colorama import Fore, Back, Style
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.support.wait import WebDriverWait
import win32com.client as comclt
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import json
import ffmpeg
import time

m3u8_url = None

# Initialize WebDriver with options (e.g., headless mode)

options = webdriver.ChromeOptions()

# options.add_argument('--headless') # Run in headless mode for no UI

options.add_argument('--start-maximized') # Run in maximized mode for no UI

options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

driver = webdriver.Chrome(options=options)
driver.implicitly_wait(10)

driver.get("https://www.lookmovie2.to/shows/play/1701831559-smiling-friends-2020#S1-E1-159353")

def close_ad_button_if_exists(driver):
    try:
        close_ad_button = WebDriverWait(driver, 12).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "pre-init-ads--close"))
        )

        close_ad_button.click()    
    except:
        print("Click interceptado....", Fore.RED)

        close_ad_button_if_exists(driver)

        raise Exception("Não foi possível encontrar o botão de fechar anúncio!")
    

close_ad_button_if_exists(driver)

m3u8_urls = []

time.sleep(5)

# with open('out.txt', 'a') as file:
#     for entry in driver.get_log('performance'):
#         # Parse the JSON message from the log entry
#         file.write(str(entry) + "\n")

logs = []

def download_m3u8_from_url(url):
    ffmpeg.input(url).output('output.mp4').run()

for entry in driver.get_log('performance'):
    message = json.loads(entry['message'])

    log_message = message.get("message", {})
    method = log_message.get("method")
    url = None

    if "Network.responseReceived" == method:
        url = log_message.get("params", {}).get("response", {}).get("url")
    elif "Network.requestWillBeSent" == method:
        url = log_message.get("params", {}).get("request", {}).get("url")

    if url and '.m3u8' in url:
        m3u8_urls.append(url)
    

print(m3u8_urls)

if url and '.m3u8' in url:
    # download_m3u8_from_url(url)
    driver.quit()


from colorama import Fore, Back, Style
from dotenv import load_dotenv
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
import os
import ffmpeg
import smtplib
import time
from util import *
from urllib.parse import urlparse



def print_status(message, status=Fore.GREEN):
    symbol = ""
    
    if status == Fore.GREEN:
        symbol = "✅ "
    elif status == Fore.RED:
        symbol = "❌ " + " "
    elif status == Fore.YELLOW:
        symbol = "⚠️ " + " "
    else:
        symbol = "ℹ️ " + " "

    print(f"{symbol}{status}{message}{Style.RESET_ALL}")


def close_ad_button_if_exists(driver):
    try:
        close_ad_button = WebDriverWait(driver, 12).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "pre-init-ads--close"))
        )

        close_ad_button.click()    
    except:
        print_status("Click interceptado....", Fore.RED)

        close_ad_button_if_exists(driver)

        raise Exception("Não foi possível encontrar o botão de fechar anúncio!")


def close_popup_if_exists(driver):
    try:
        # Find all elements with the specific class name
        elements_to_hide = driver.find_elements(By.CLASS_NAME, "notifyjs-black_notify-base")

        # Iterate and hide each element using JavaScript
        for element in elements_to_hide:
            driver.execute_script("arguments[0].style.display = 'none';", element)
    except:
        print_status("Popup não encontrado!", Fore.YELLOW)

        return 


def pause_video(driver):
    time.sleep(5)

    pause_button = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CLASS_NAME, "notifyjs-prem_notify-base"))
    )

    pause_button.click()

    print_status("Vídeo pausado!", Fore.GREEN)


def get_episode_links(file):
    with open(file, 'r') as file:
        return file.read().splitlines()


def get_filename_from_url(url):
    """
    Extracts a filename from a lookmovie2 URL (e.g., 'smiling-friends-S1-E1').

    Args:
        url (str): The URL of the episode page.

    Returns:
        str: A clean filename or None if the format is incorrect.
    """
    try:
        parsed_url = urlparse(url)
        show_info = parsed_url.path.strip('/').split('/')[-1]
        show_name = '-'.join(show_info.split('-')[1:-1])
        episode_identifier = '-'.join(parsed_url.fragment.split('-')[:2])
        
        if show_name and episode_identifier:
            return f"{show_name}-{episode_identifier}"
    except (IndexError, AttributeError):
        pass
    return None


def download_episode_from_url(url, driver):
    print_status("Abrindo página...", Fore.YELLOW)

    driver.switch_to.new_window('tab')

    driver.get(url)

    filename = get_filename_from_url(url)

    if not filename:
        print_status(f"Não foi possível extrair o nome do episódio da URL: {url}", Fore.RED)
        return
    
    print_status(f"Baixando episódio \"{filename}\"", Fore.BLUE)

    print_status("Fechando anúncio...", Fore.YELLOW)

    close_ad_button_if_exists(driver)
    close_popup_if_exists(driver)

    print_status("Anúncio fechado!", Fore.GREEN)

    # pause_video(driver)

    time.sleep(5)

    url = get_m3u8_url(driver)

    download_m3u8_from_url(url=url, filename=filename)

    print_status(f"Episódio {str(filename)} baixado com sucesso!", Fore.GREEN)

    send_status_email(f"Baixou {filename}", f"Episodio {filename} baixado com sucesso!")


def get_m3u8_url(driver):
    """
    Parses the performance logs from the WebDriver to find the .m3u8 URL.
    """

    print_status("Analyzing logs for .m3u8 URL...", Fore.YELLOW)

    for entry in driver.get_log('performance'):
        message = json.loads(entry['message'])
        log_message = message.get("message", {})
        method = log_message.get("method")

        url = None
        if "Network.requestWillBeSent" == method:
            url = log_message.get("params", {}).get("request", {}).get("url")
        elif "Network.responseReceived" == method:
            url = log_message.get("params", {}).get("response", {}).get("url")

        if url and '.m3u8' in url:
            print_status(f"Found .m3u8 URL: {url}", Fore.GREEN)
            return url

    print_status("Could not find .m3u8 URL in performance logs.", Fore.RED)
    return None


def download_m3u8_from_url(url, filename, base_folder = "D:\\Downloads\\"):
    try:
        ffmpeg.input(url).output(base_folder + filename + '.mp4', vcodec='libx264', acodec='aac', preset="slow").overwrite_output().run()
    except Exception as e:
        print_status(f"Erro na conversão do FFMPEG: {e} Tentando de novo...", Fore.RED)

        ffmpeg.input(url).output(base_folder + filename + '.mp4', vcodec='libx264', acodec='aac', preset="slow").overwrite_output().run()


def close_all_tabs_except_current(driver):
    curr = driver.current_window_handle

    for handle in driver.window_handles:
        driver.switch_to.window(handle)

        if handle != curr:
            driver.close()


def download_episodes(episodes_url, driver):
    for url in episodes_url:
        download_episode_from_url(url, driver)

        episode_name = get_filename_from_url(url)

        executar_tarefa_com_alerta(
            download_episode_from_url,
            f"Baixar episodio: {episode_name}",
            max_retries=3,
            retry_delay_sec=5,
            url=url,
            driver=driver
        )

        close_all_tabs_except_current(driver)

def main():
    print_status("Iniciando Scraper...", Fore.GREEN)

    print_status("Definindo Configurações...", Fore.YELLOW)

    options = webdriver.ChromeOptions()

    options.add_argument("--mute-audio")
    # options.add_argument('--headless') # Run in headless mode for no UI
    # options.add_argument('--start-maximized') # Run in maximized mode for no UI

    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)

    episodes_url = get_episode_links('missing-adventure-time-episodes.txt')

    print_status(f"{len(episodes_url)} episodios encontrados!", Fore.GREEN)

    print_status("Iniciando download...", Fore.YELLOW)

    send_status_email("Iniciando scraper!", f"{str(len(episodes_url))} episodios encontrados!")

    driver.minimize_window()

    download_episodes(episodes_url=episodes_url, driver=driver)

    print_status("Scraper finalizado!", Fore.GREEN)

    driver.quit()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_status("Interrompido pelo usuário!", Fore.RED)


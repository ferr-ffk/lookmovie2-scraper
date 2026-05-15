# Entra no primeiro episódio da série (link dado)
# Vai na aba de temporadas e vai pegando episódio por episódio
# Salva os links de cada página no arquivo

from colorama import Fore
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from util import *
import logging
from selenium.webdriver.remote.remote_connection import LOGGER
from selenium.common.exceptions import ElementClickInterceptedException


def check_if_ad_button_exists(driver):
    try:
        WebDriverWait(driver, 1).until(
            EC.element_to_be_clickable((By.XPATH, "//a[@href='/premium.html']"))
        )

        return True
    except:
        return False


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
    

def get_episode_links(first_episode_url, output_file="episode-links.txt"):
    episode_links: list[str] = []

    print_status("Iniciando Scraper...", Fore.GREEN)

    print_status("Definindo Configurações...", Fore.YELLOW)

    options = webdriver.ChromeOptions()
    # options.add_argument('--headless') # Run in headless mode for no UI
    # options.add_argument('--start-maximized') # Run in maximized mode for no UI
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)

    print_status("Abrindo página inicial...", Fore.BLUE)

    driver.get(first_episode_url)

    # print_status("Aplicando zoom para ter certeza que anúncios não ficarão no caminho...", Fore.YELLOW)
    # driver.execute_script("document.body.style.zoom = '0.4'")

    print_status("Fechando anúncio...", Fore.YELLOW)

    close_ad_button_if_exists(driver)
    close_popup_if_exists(driver)

    print_status("Anúncio fechado!", Fore.GREEN)

    print_status("Obtendo cada link...", Fore.YELLOW)

    open_seasons_episodes_tabs(driver)

    seasons_tab_initial = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "seasons"))
    )

    episodes_tab_initial = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "episodes"))
    )

    seasons_items = seasons_tab_initial.find_elements(By.TAG_NAME, "li")
    episodes_items_by_current_season_selected = episodes_tab_initial.find_elements(By.TAG_NAME, "li")

    print(f"Total de temporadas: {len(seasons_items)}")
    print(f"Total de episódios da temporada \"{seasons_items[0].text}\": {len(episodes_items_by_current_season_selected)}")

    for season_number in range(len(seasons_items)):
        print_status(f"Abrindo episódios da temporada {season_number + 1}...", Fore.BLUE)

        ad_exists = check_if_ad_button_exists(driver)

        if ad_exists:
            print_status("Anúncio encontrado! Fechando...", Fore.YELLOW)
            close_ad_button_if_exists(driver)

        close_popup_if_exists(driver)

        if season_number != 0:
            try:
                open_seasons_episodes_tabs(driver, open_episodes_tab=True, open_seasons_tab=True)
            except:
                print_status("Click interceptado... Tentando de novo...", Fore.RED)

                close_ad_button_if_exists(driver)

                open_seasons_episodes_tabs(driver, open_episodes_tab=True, open_seasons_tab=True)


        try:
            seasons_tab = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "seasons"))
            )
        except:
            print_status("Não foi possível encontrar a aba de temporadas! Tentando de novo...", Fore.RED)

            open_seasons_episodes_tabs(driver, open_seasons_tab=True)

            seasons_tab = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "seasons"))
            )        

        seasons_items = seasons_tab.find_elements(By.TAG_NAME, "li")
        seasons_items[season_number].click()

        for episode_number in range(len(episodes_items_by_current_season_selected)):
            print_status(f"Abrindo episódio {episode_number + 1}...", Fore.BLUE)

            ad_exists = check_if_ad_button_exists(driver)

            if episode_number == 0:
                ad_exists = False # Impossivel um anuncio tocar no primeiro episodio, pois já foi fechado anteriormente

            if ad_exists:
                print_status("Anúncio encontrado! Fechando...", Fore.YELLOW)

                close_ad_button_if_exists(driver)
            else:
                print_status("Anúncio não encontrado! Prosseguindo...", Fore.YELLOW)


            close_popup_if_exists(driver)


            is_first_episode = episode_number == 0

            is_first_season = season_number == 0


            try:
                open_seasons_episodes_tabs(driver, open_episodes_tab=not is_first_episode, open_seasons_tab=is_first_season)
            except:
                print_status("Click interceptado...", Fore.RED)

                close_ad_button_if_exists(driver)

                open_seasons_episodes_tabs(driver, open_episodes_tab=not is_first_episode, open_seasons_tab=is_first_season)

            try:
                episodes_tab = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "episodes"))
                )
            except:
                print_status("Não foi possível encontrar a aba de episódios! Tentando de novo...", Fore.RED)

                open_seasons_episodes_tabs(driver, open_episodes_tab=True)

                episodes_tab = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "episodes"))
                )

            episodes_items_by_current_season_selected = episodes_tab.find_elements(By.TAG_NAME, "li")

            try:
                episodes_items_by_current_season_selected[episode_number].click()
            except IndexError:
                print_status("Por algum motivo o driver tentou clicar num n° de episódio que não existe! Prosseguindo...", Fore.RED)
                break
            except Exception:
                print_status("Click interceptado... Tentando de novo")

                close_ad_button_if_exists(driver)

                episodes_items_by_current_season_selected[episode_number].click()

            episode_url = driver.current_url
            episode_links.append(episode_url)

            print_status("Episódio encontrado: " + episode_url)

    print_status(f"{len(episode_links)} episódios encontrados!", Fore.GREEN)

    print_status("Salvando links...", Fore.YELLOW)

    with open(output_file, 'w') as file:
        for link in episode_links:
            file.write(link + '\n')

    print_status("Scraper finalizado!", Fore.GREEN)

    driver.quit()


def open_seasons_episodes_tabs(driver, open_episodes_tab=True, open_seasons_tab=True):
    seasons_switcher = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "seasons-switcher"))
    )

    episodes_switcher = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "episodes-switcher"))
    )

    try:
        # Clica nas duas tabs para expandir a lista
        if open_episodes_tab:
            episodes_switcher.click()

        if open_seasons_tab:
            seasons_switcher.click()
    except ElementClickInterceptedException as e:
        print_status("Click interceptado ao expandir abas de episódios e temporadas! Tentando de novo...", Fore.RED)

        send_status_email("Click interceptado!", "Click interceptado ao expandir abas de episodios e temporadas! Tentando de novo...")

        close_ad_button_if_exists(driver)

        # Clica nas duas tabs para expandir a lista
        if open_episodes_tab:
            episodes_switcher.click()

        if open_seasons_tab:
            seasons_switcher.click()

    return


if __name__ == "__main__":
    LOGGER.setLevel(logging.ERROR)

    if len(sys.argv) < 3:
        print("Usage: python [link] [episodios.txt]")
        sys.exit(1)

    try:
        first_episode = sys.argv[1]
        episodes_filename = sys.argv[2]

        send_status_email("Iniciando scraper de 'get-video-links'...", f"Os episodios serao salvos em {episodes_filename}.")

        get_episode_links(first_episode, episodes_filename)

        send_status_email("Lista de Episodios salvos!", f"Lista de episodios salvos em \'{episodes_filename}\'.")
    except KeyboardInterrupt:
        print_status("Interrompido pelo usuário!", Fore.RED)
        sys.exit(1)
    except Exception as e:
        print_status(f"Erro inesperado: {e}", Fore.RED)

        send_status_email("Erro inesperado ao obter link dos episodios!", f"Erro inesperado: {e}")
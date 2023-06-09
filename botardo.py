from os import getcwd
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options


def main():
    pass


def get_elements(html: str) -> tuple:
    soup = BeautifulSoup(html, "html.parser")

    day = soup.find(id="js-faltan")
    name = soup.find(id="js-detalle")
    date = soup.find(id="js-proximo")

    return day.text, name.text, date.text


def get_html() -> str:
    url = "https://www.argentina.gob.ar/interior/feriados-nacionales-2023"

    webdriver_path = f'{getcwd()}/chromedriver'

    # Launch Chrome with the profile and load the URL
    options = Options()
    options.page_load_strategy = 'normal'
    options.add_argument('--headless')

    driver = webdriver.Chrome(options=options)
    driver.get(url)

    # Get the page source after JavaScript rendering
    page_source = driver.page_source

    # Close the browser
    driver.quit()

    return page_source


def get_tweet() -> str:
    days_left, feriado_name, date_str = get_elements(get_html())
    tweet = ""
    if days_left == "0":
        tweet += f"Hoy es feriado!\n\n"
        tweet += f"⁉️{feriado_name}"

    elif days_left == "1":
        tweet += f"Mañana es feriado! 🔜\n\n"
        tweet += f"⁉️{feriado_name}"

    else:
        tweet += f"Faltan {days_left} días para el próximo feriado.\n"
        tweet += f"Será el {date_str}.\n\n"
        tweet += f"⁉️{feriado_name}"

    return tweet


if __name__ == '__main__':
    main()
    print(get_tweet())

import datetime
from os import getcwd
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from requests_oauthlib import OAuth1Session
from json import dumps
from os import getenv, environ
from time import sleep


def main():
    load_env_variables()
    consumer_key = getenv("TW_CONSUMER_KEY")
    consumer_secret = getenv("TW_CONSUMER_SECRET")
    oauth_token = getenv("TW_OAUTH_TOKEN")
    oauth_token_secret = getenv("TW_OAUTH_TOKEN_SECRET")

    while True:
        print("Running...")
        sleep_until_next_tweet()
        make_tweet(consumer_key, consumer_secret, oauth_token, oauth_token_secret)


def make_tweet(consumer_key: str, consumer_secret: str, oauth_token: str, oauth_token_secret: str) -> None:

    payload = {"text": get_tweet_content()}

    # Make the request
    oauth = OAuth1Session(
        consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=oauth_token,
        resource_owner_secret=oauth_token_secret,
    )

    # Making the request
    response = oauth.post(
        "https://api.twitter.com/2/tweets",
        json=payload,
    )

    if response.status_code != 201:
        raise Exception(
            "Request returned an error: {} {}".format(response.status_code, response.text)
        )

    print("Response code: {}".format(response.status_code))

    # Saving the response as JSON
    json_response = response.json()
    print(dumps(json_response, indent=4, sort_keys=True))


def sleep_until_next_tweet():
    # Get the current datetime in UTC-3
    current_datetime = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3)))

    # Set the target datetime for the next day at 9 AM
    target_datetime = current_datetime.replace(hour=9, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)

    # Calculate the time difference between the current and target datetime
    time_difference = target_datetime - current_datetime

    # Convert the time difference to seconds
    sleep_duration = time_difference.total_seconds()

    print(f"Sleeping for {sleep_duration} seconds")
    # Sleep until the target datetime
    sleep(sleep_duration)


def load_env_variables():
    with open(".env", 'r') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                environ[key] = value


def get_elements(html: str) -> tuple:
    soup = BeautifulSoup(html, "html.parser")

    day = soup.find(id="js-faltan")
    name = soup.find(id="js-detalle")
    date = soup.find(id="js-proximo")

    return day.text, name.text, date.text


def get_html() -> str:
    url = "https://www.argentina.gob.ar/interior/feriados-nacionales-2023"

    webdriver_path = f'{getcwd()}/webdriver'

    # Launch Chrome with the profile and load the URL
    options = Options()
    options.page_load_strategy = 'normal'
    options.add_argument(f"--user-data-dir={webdriver_path}")
    options.add_argument('--headless')

    driver = webdriver.Chrome(options=options)
    driver.get(url)

    # Get the page source after JavaScript rendering
    page_source = driver.page_source

    # Close the browser
    driver.quit()

    return page_source


def fancy_days_left(days_left: str) -> str:
    fancy_mapping = {
        "0": "0️⃣",
        "1": "1️⃣",
        "2": "2️⃣",
        "3": "3️⃣",
        "4": "4️⃣",
        "5": "5️⃣",
        "6": "6️⃣",
        "7": "7️⃣",
        "8": "8️⃣",
        "9": "9️⃣"
    }
    fancy_days_left = "".join(fancy_mapping.get(number, "") for number in days_left)

    return fancy_days_left


def get_tweet_content() -> str:
    days_left, feriado_name, date_str = get_elements(get_html())
    days_left = fancy_days_left(days_left)
    tweet = ""
    if days_left == "0":
        tweet += f"Hoy es feriado!\n\n"
        tweet += f"⁉️{feriado_name}"

    elif days_left == "1":
        tweet += f"Mañana es feriado! 🔜\n\n"
        tweet += f"⁉️{feriado_name}"

    else:
        tweet += f"Faltan {days_left} días para el próximo feriado\n\n"
        tweet += f"🗓️ {date_str}\n\n"
        tweet += f"⁉️ {feriado_name}"

    return tweet


if __name__ == '__main__':
    main()

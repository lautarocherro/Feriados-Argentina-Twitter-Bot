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
    load_env_variables('.env')
    consumer_key = getenv("TW_CONSUMER_KEY")
    consumer_secret = getenv("TW_CONSUMER_SECRET")

    while True:
        sleep_until_next_tweet()
        make_tweet(consumer_key, consumer_secret)


def sleep_until_next_tweet():
    # Get the current datetime in UTC-3
    current_datetime = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3)))

    # Set the target datetime for the next day at 9 AM
    target_datetime = current_datetime.replace(hour=9, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)

    # Calculate the time difference between the current and target datetime
    time_difference = target_datetime - current_datetime

    # Convert the time difference to seconds
    sleep_duration = time_difference.total_seconds()

    # Sleep until the target datetime
    sleep(sleep_duration)


def load_env_variables(file_path):
    with open(file_path, 'r') as f:
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


def make_tweet(consumer_key: str, consumer_secret: str) -> bool:
    # Content to tweet
    payload = {"text": get_tweet()}

    # Get request token
    request_token_url = "https://api.twitter.com/oauth/request_token?oauth_callback=oob&x_auth_access_type=write"
    oauth = OAuth1Session(consumer_key, client_secret=consumer_secret)
    fetch_response = None

    try:
        fetch_response = oauth.fetch_request_token(request_token_url)
    except ValueError:
        print(
            "There may have been an issue with the consumer_key or consumer_secret you entered."
        )

    resource_owner_key = fetch_response.get("oauth_token")
    resource_owner_secret = fetch_response.get("oauth_token_secret")
    print("Got OAuth token: %s" % resource_owner_key)

    # Get authorization
    base_authorization_url = "https://api.twitter.com/oauth/authorize"
    authorization_url = oauth.authorization_url(base_authorization_url)
    print("Please go here and authorize: %s" % authorization_url)
    verifier = input("Paste the PIN here: ")

    # Get the access token
    access_token_url = "https://api.twitter.com/oauth/access_token"
    oauth = OAuth1Session(
        consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=resource_owner_key,
        resource_owner_secret=resource_owner_secret,
        verifier=verifier,
    )
    oauth_tokens = oauth.fetch_access_token(access_token_url)

    access_token = oauth_tokens["oauth_token"]
    access_token_secret = oauth_tokens["oauth_token_secret"]

    # Make the request
    oauth = OAuth1Session(
        consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=access_token,
        resource_owner_secret=access_token_secret,
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

    return True


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
        tweet += f"Faltan {days_left} días para el próximo feriado.\n\n"
        tweet += f"📆 {date_str}\n\n"
        tweet += f"⁉️ {feriado_name}"

    return tweet


if __name__ == '__main__':
    main()

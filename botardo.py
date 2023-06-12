from datetime import datetime, timezone, timedelta
from json import dumps
from os import getenv, environ
from time import sleep
import pytz
from util import month_mapping, fancy_mapping, weekday_mapping

from requests import get as get_request
from requests_oauthlib import OAuth1Session
import pandas as pd


def load_env_variables():
    with open(".env", 'r') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                environ[key] = value


def sleep_until_next_tweet():
    # Get the current datetime in UTC-3
    current_datetime = datetime.now(timezone(timedelta(hours=-3)))

    # Set the target datetime for the next day at 9 AM
    target_datetime = current_datetime.replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=1)

    # Calculate the time difference between the current and target datetime
    time_difference = target_datetime - current_datetime

    # Convert the time difference to seconds
    sleep_duration = time_difference.total_seconds()

    print(f"Sleeping for {sleep_duration} seconds")
    # Sleep until the target datetime
    sleep(sleep_duration)


class HolidayInfo:
    def __init__(self):
        self.date_str = None
        self.tweet_content = None
        self.fancy_days_left = None
        self.days_left = None
        self.next_holiday_weekday = None
        self.next_holiday_reason = None
        self.next_holiday_year = None
        self.next_holiday_month = None
        self.next_holiday_day = None
        self.holidays = None

        load_env_variables()
        self.consumer_key = getenv("TW_CONSUMER_KEY")
        self.consumer_secret = getenv("TW_CONSUMER_SECRET")
        self.oauth_token = getenv("TW_OAUTH_TOKEN")
        self.oauth_token_secret = getenv("TW_OAUTH_TOKEN_SECRET")

    def run(self):
        while True:
            print("Running...")
            sleep_until_next_tweet()
            self.make_tweet()

    def make_tweet(self):

        # Set Tweet's content
        self.set_tweet_content()

        payload = {"text": self.tweet_content}

        # Make the request
        oauth = OAuth1Session(
            self.consumer_key,
            client_secret=self.consumer_secret,
            resource_owner_key=self.oauth_token,
            resource_owner_secret=self.oauth_token_secret,
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

    def process_holidays(self):

        # First, get the Holidays DataFrame
        self.set_holidays()
        # Get the current datetime in UTC-3
        timezone = pytz.timezone('America/Argentina/Buenos_Aires')
        now = datetime.now(timezone).replace(tzinfo=None)  # Convert to offset-naive datetime

        # Get future holidays (including today)
        future_holidays_df = self.holidays[
            (self.holidays["year"] >= now.year) &
            (self.holidays["mes"] >= now.month) &
            (self.holidays["dia"] >= now.day)]

        # Get the next holiday
        next_holiday = future_holidays_df.iloc[0]

        # Get next holiday date info
        self.next_holiday_day = next_holiday["dia"]
        self.next_holiday_month = next_holiday["mes"]
        self.next_holiday_year = next_holiday["year"]
        self.next_holiday_reason = next_holiday["motivo"]

        # Get days left to next holiday
        self.days_left = (datetime(self.next_holiday_year, self.next_holiday_month, self.next_holiday_day) - now).days \
                         + 1  # Add 1 to include today
        # Set weekday
        self.set_weekday()

    def set_holidays(self):
        # Get current year
        year = datetime.now().year

        current_year_url = f"https://nolaborables.com.ar/api/v2/feriados/{year}"
        next_year_url = f"https://nolaborables.com.ar/api/v2/feriados/{year + 1}"

        # Make the requests
        current_year_response = get_request(current_year_url)
        next_year_response = get_request(next_year_url)

        if current_year_response.status_code != 200 or next_year_response.status_code != 200:
            raise Exception(
                "Request returned an error: {} {}".format(current_year_response.status_code, current_year_response.text)
            )

        # Convert responses to JSON
        current_year_json = current_year_response.json()
        next_year_json = next_year_response.json()

        # Convert the response to a DataFrame for this year
        self.holidays = pd.DataFrame(current_year_json).drop(columns=["info", "id", "original", "tipo"])
        # Add column year
        self.holidays["year"] = year

        # Convert the response to a DataFrame for next year
        next_year_holidays = pd.DataFrame(next_year_json).drop(columns=["info", "id", "original", "tipo"])
        # Add column year
        next_year_holidays["year"] = year + 1

        # Concatenate the holidays from next year
        self.holidays = pd.concat([self.holidays, next_year_holidays])

    def set_weekday(self):
        # Get the current datetime in UTC-3
        current_datetime = datetime.now(timezone(timedelta(hours=-3))) \
                           + timedelta(days=int(self.days_left))

        weekday = current_datetime.strftime("%A")

        self.next_holiday_weekday = weekday_mapping.get(weekday, "")

    def set_fancy_days_left(self):
        self.fancy_days_left = "".join(fancy_mapping.get(number, "") for number in str(self.days_left))

    def set_date_str(self):
        self.date_str = f"{self.next_holiday_weekday} {self.next_holiday_day}" \
                        f" de {month_mapping.get(self.next_holiday_month, '')} de {self.next_holiday_year}"

    def set_tweet_content(self):
        # First process Holiday's info
        self.process_holidays()

        self.tweet_content = ""

        if self.days_left == 0:
            self.tweet_content += f"Hoy es feriado!\n\n"
            self.tweet_content += f"⁉️{self.next_holiday_reason}"

        elif self.days_left == 1:
            self.tweet_content += f"Mañana es feriado! 🔜\n\n"
            self.tweet_content += f"⁉️{self.next_holiday_reason}"

        else:
            # Set variables exlusive for this case
            self.set_date_str()
            self.set_fancy_days_left()

            self.tweet_content += f"Faltan {self.fancy_days_left} días para el próximo feriado\n\n"
            self.tweet_content += f"🗓️ {self.date_str}\n\n"
            self.tweet_content += f"⁉️ {self.next_holiday_reason}"

        return self.tweet_content


if __name__ == '__main__':
    HolidayInfo().run()

from datetime import datetime, timedelta
from json import dumps
from os import getenv

import pandas as pd
import pytz
from requests import get as get_request
from requests_oauthlib import OAuth1Session

from util import sleep_until_next_tweet, load_env_variables, get_date_str, get_fancy_numbers


class HolidayInfo:
    def __init__(self):
        self.weekend_length = None
        self.first_weekend_date = None
        self.last_weekend_date = None
        self.next_holiday = None
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
        print("Running...")

        while True:
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
        self.holidays = pd.concat([self.holidays, next_year_holidays]).reset_index(drop=True)

        # Create a new column with the date as a datetime object
        self.holidays["date"] = self.holidays.apply(
            lambda row: datetime(year=row["year"], month=row["mes"], day=row["dia"], hour=23, minute=59, second=59),
            axis=1
        )

        # Create a new column with each day's weekday
        self.holidays["weekday"] = self.holidays.apply(
            lambda row: row["date"].strftime("%A"),
            axis=1
        )

    def process_holidays(self):

        # First, get the Holidays DataFrame
        self.set_holidays()
        # Get the current datetime in UTC-3
        timezone = pytz.timezone('America/Argentina/Buenos_Aires')
        now = datetime.now(timezone).replace(tzinfo=None)  # Convert to offset-naive datetime

        # Get future holidays (including today)
        future_holidays_df = self.holidays[self.holidays["date"] >= now]

        # Get the next holiday
        self.next_holiday = future_holidays_df.iloc[0]

        # Get next holiday date info
        self.next_holiday_day = self.next_holiday["dia"]
        self.next_holiday_month = self.next_holiday["mes"]
        self.next_holiday_year = self.next_holiday["year"]
        self.next_holiday_reason = self.next_holiday["motivo"]
        self.next_holiday_weekday = self.next_holiday["weekday"]

        # Get days left to next holiday and add 1 to include today
        self.days_left = (datetime(self.next_holiday_year, self.next_holiday_month, self.next_holiday_day)
                          - now).days + 1

        self.process_long_weekends()

    def process_long_weekends(self):
        next_holiday_date = self.next_holiday["date"]

        # Set first and last weekend dates
        self.set_first_weekend_date(next_holiday_date)
        self.set_last_weekend_date(self.first_weekend_date)

        # Get the number of days between the first and last weekend dates
        self.weekend_length = (self.last_weekend_date - self.first_weekend_date).days + 1

    def set_first_weekend_date(self, date):
        # Check if the day before of next_holiday is a holiday or weekend
        day_before = date - timedelta(days=1)
        if day_before.weekday() > 4 or day_before in self.holidays["date"].values:
            self.set_first_weekend_date(day_before)
        else:
            self.first_weekend_date = date

    def set_last_weekend_date(self, date):
        # Check if the day after of date is a holiday or weekend
        day_after = date + timedelta(days=1)
        if day_after.weekday() > 4 or day_after in self.holidays["date"].values:
            self.set_last_weekend_date(day_after)
        else:
            self.last_weekend_date = date

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
            date_str = get_date_str(self.next_holiday_weekday, self.next_holiday_day, self.next_holiday_month,
                                    self.next_holiday_year)

            self.tweet_content += f"Faltan {get_fancy_numbers(self.days_left)} días para el próximo feriado:\n\n"
            self.tweet_content += f"🗓️ {date_str}\n"
            self.tweet_content += f"⁉️ {self.next_holiday_reason}"

        if self.weekend_length > 2:
            weekend_start_date_str = get_date_str(self.first_weekend_date.strftime("%A"),
                                                  self.first_weekend_date.day,
                                                  self.first_weekend_date.month,
                                                  self.first_weekend_date.year)

            weekend_end_date_str = get_date_str(self.last_weekend_date.strftime("%A"),
                                                self.last_weekend_date.day,
                                                self.last_weekend_date.month,
                                                self.last_weekend_date.year)

            self.tweet_content += f"\n\n\nSerá un fin de semana de {get_fancy_numbers(self.weekend_length)} días:\n\n"
            self.tweet_content += f"📈 Desde el {weekend_start_date_str}\n"
            self.tweet_content += f"📉 Hasta el {weekend_end_date_str}"

        return self.tweet_content


if __name__ == '__main__':
    HolidayInfo().run()

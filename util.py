from datetime import datetime, timezone, timedelta
from os import environ
from time import sleep

month_mapping = {
    1: "Enero",
    2: "Febrero",
    3: "Marzo",
    4: "Abril",
    5: "Mayo",
    6: "Junio",
    7: "Julio",
    8: "Agosto",
    9: "Septiembre",
    10: "Octubre",
    11: "Noviembre",
    12: "Diciembre"
}

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

sad_emoji_list = ("🙄", "😒", "😔", "😢", "😭", "😤", "😐", "🥱", "💀", "⚰️", "🤡")
weekday_mapping = {
    "Sunday": f"Domingo",
    "Monday": "Lunes",
    "Tuesday": "Martes",
    "Wednesday": "Miércoles",
    "Thursday": "Jueves",
    "Friday": "Viernes",
    "Saturday": f"Sábado"
}


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

    print(f"Sleeping for {sleep_duration} seconds. Next tweet will be at {target_datetime}")
    # Sleep until the target datetime
    sleep(sleep_duration)


def get_date_str(weekday, day, month, year) -> str:
    return f"{weekday_mapping.get(weekday, '')} {day} de {month_mapping.get(month, '')} de {year}"


def get_fancy_numbers(days: int) -> str:
    return "".join(fancy_mapping.get(number, "") for number in str(days))
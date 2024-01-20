from datetime import datetime, timedelta

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


def get_date_str(weekday, day, month, year) -> str:
    return f"{weekday_mapping.get(weekday, '')} {day} de {month_mapping.get(month, '')} de {year}"


def get_fancy_numbers(days: int) -> str:
    return "".join(fancy_mapping.get(number, "") for number in str(days))


def get_now_arg():
    # Get the current UTC time
    utc_now = datetime.utcnow()

    # Define a timedelta for UTC - 3 hours
    utc_minus_3_delta = timedelta(hours=-3)

    # Calculate the UTC - 3 time by subtracting the timedelta
    utc_minus_3_time = utc_now + utc_minus_3_delta

    return utc_minus_3_time

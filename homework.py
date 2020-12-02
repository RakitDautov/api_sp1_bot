import os
import time

import requests
import telegram
from dotenv import load_dotenv
import logging

load_dotenv()


PRAKTIKUM_TOKEN = os.getenv("PRAKTIKUM_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_URL = "https://praktikum.yandex.ru/api/user_api/homework_statuses/"


def parse_homework_status(homework):
    if homework.get("homework_name") and homework.get("status"):
        homework_name = homework.get("homework_name")
        homework_status = homework.get("status")
    else:
        return "Ошибка запроса 'homework.get'"
    if homework_status != "approved":
        verdict = "К сожалению в работе нашлись ошибки."
    else:
        verdict = (
            "Ревьюеру всё понравилось, можно приступать к следующему уроку."
        )
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    headers = {"Authorization": f"OAuth {PRAKTIKUM_TOKEN}"}
    if current_timestamp is None:
        current_timestamp = int(time.time())
    params = {"from_date": current_timestamp}
    try:
        homework_statuses = requests.get(
            API_URL, headers=headers, params=params
        )
        return homework_statuses.json()
    except Exception as e:
        logging.error(f"Error {e} at request on server practicum", exc_info=e)


def send_message(message, bot_client):
    return bot_client.send_message(chat_id=CHAT_ID, text=message)


def main():
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get("homeworks"):
                send_message(
                    parse_homework_status(new_homework.get("homeworks")[0]),
                    bot_client=bot,
                )
            current_timestamp = new_homework.get(
                "current_date", current_timestamp
            )
            time.sleep(1200)

        except requests.exceptions.RequestException as e:
            print(f"Бот столкнулся с ошибкой: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()

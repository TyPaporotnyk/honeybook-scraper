from scraper.notifications.honeybook import HoneyBook
from scraper.scrape.scrape import parse
from connection.connection import DBConnector
import requests

from config import BOT_TOKEN, CHAT_IDS


def send_to_telegram(message: str) -> None:
    apiURL = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'

    for chat_id in CHAT_IDS:
        params = {
            'chat_id': chat_id,
            'text': message
        }

        try:
            response = requests.post(apiURL, json=params)
        except Exception as e:
            print(e)


def get_leeds() -> list:
    HoneyBook.Instance().getAllNotifications()
    parse()

    return DBConnector.Instance().get_new_leeds()


def print_leads(leeds : list) -> None:
    for leed in leeds:
        message = f"New opportunity near {leed[1]} for {leed[2]}, published by " \
                f"{leed[3]}.\nFollow the link for details - https://artlook.us/leads/?id={leed[0]}"
        send_to_telegram(message=message)

if __name__ == '__main__':
    print_leads(get_leeds())
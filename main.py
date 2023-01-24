from honeybook import HoneyBook, getDataFromNotif
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

        response = requests.post(apiURL, json=params)
        try:
            response.raise_for_status()
        except Exception as e:
            print(e)


def get_leeds() -> list:
    user_api = HoneyBook()
    client_information = getDataFromNotif(user_api)

    for client in client_information:
        DBConnector.Instance().store_db(client)


def print_leads() -> None:
    leeds = DBConnector.Instance().get_new_leeds()
    for leed in leeds:
        message = f"New opportunity near {leed[1]} for {leed[2]}, published by " \
                f"{leed[3]}.\nFollow the link for details - https://artlook.us/leads/?id={leed[0]}"
        send_to_telegram(message=message)

if __name__ == '__main__':
    get_leeds()
    print_leads()

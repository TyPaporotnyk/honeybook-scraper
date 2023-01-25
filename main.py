from honeybook import HoneyBook, getDataFromNotif
from connection.connection import DBConnector
from utils import create_logger
import requests

from config import BOT_TOKEN, CHAT_IDS

logger = create_logger('Main')

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
            logger.error('Ошибка при выводе сообщения в Телеграмм')


def get_leeds() -> list:
    user_api = HoneyBook()
    client_information = getDataFromNotif(user_api)

    for client in client_information:
        DBConnector.Instance().store_db(client)
    logger.info('Данные были загружены в базу данных')


def print_leads() -> None:
    leeds = DBConnector.Instance().get_new_leeds()
    for leed in leeds:
        message = f"New opportunity near {leed[1]} for {leed[2]}, published by " \
                f"{leed[3]}.\nFollow the link for details - https://artlook.us/leads/?id={leed[0]}"
        send_to_telegram(message=message)

if __name__ == '__main__':
    get_leeds()
    # print_leads()

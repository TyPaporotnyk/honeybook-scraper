import requests
from requests import HTTPError

from config import BOT_TOKEN, CHAT_IDS
from utils import create_logger

logger = create_logger(__name__)


def send_to_telegram(message: str):
    """
    Sends a message to telegram chats
    """
    api_url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'

    for chat_id in CHAT_IDS:
        params = {
            'chat_id': chat_id,
            'text': message
        }

        response = requests.post(api_url, json=params)
        try:
            response.raise_for_status()
        except HTTPError as e:
            logger.error(f'Ошибка при выводе сообщения в Телеграмм: {repr(e)}')

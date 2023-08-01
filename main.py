from connection.connection import DBConnector
from honeybook import HoneyBook, get_data_from_notif
from telegram import send_to_telegram
from utils import create_logger

logger = create_logger(__name__)


def get_contacts():
    """
    Gets all contacts and adds up it to the database
    """
    user_api = HoneyBook()
    client_information = get_data_from_notif(user_api)

    for client in client_information:
        DBConnector.instance().store_db(client)
    logger.info('Данные были загружены в базу данных')


def print_contacts():
    """
    Send messages about collected contacts to telegram chats at last 30 minutes
    """
    leeds = DBConnector.instance().get_new_leeds()
    for lead in leeds:
        message = f"New opportunity near {lead[1]} for {lead[2]}, published by " \
                f"{lead[3]}.\nFollow the link for details - https://artlook.us/leads/?id={lead[0]}"
        send_to_telegram(message=message)


if __name__ == '__main__':
    get_contacts()
    print_contacts()

import time
from datetime import datetime
from typing import List, Optional

from fake_useragent import UserAgent
from requests import HTTPError, Session

from config import HONEYBOOK_EMAIL, HONEYBOOK_PASSWORD
from utils import (create_logger, empty_str_to_none, get_email,
                   get_phone_number, set_budget)


class AuthenticationError(Exception):
    """
    Custom authentication exception class
    """
    def __init__(self, message, errors):
        super().__init__(message)
        self.errors = errors


class HoneyBook(object):
    def __init__(self, logger=create_logger('HoneyBook')) -> None:
        self.logger = logger
        self.session = Session()
        self.session.headers.update({
            'User-Agent': UserAgent().random,
            'Host': 'api.honeybook.com',
            'Origin': 'https://www.honeybook.com',
            'Connection': 'keep-alive',
            'Accept-Language': 'ru',
            'Accept': 'application/json, text/plain, */*',
        })
        self.set_access_token()

    def set_access_token(self) -> None:
        """Получает Access token и задает его в headers"""
        json_data = {
            'password': HONEYBOOK_PASSWORD,
            'trust_device': True,
            'source': 'link',
            'sourceData': {},
            'fingerprint': 'e633423f731453fc2a9dbfc711ef43b8',
        }

        response = self.session.post(
            f'https://api.honeybook.com/api/v2/users/{HONEYBOOK_EMAIL}/tokens',
            json=json_data,
        )
        try:
            response.raise_for_status()
            self.logger.info(response)

            data = response.json()
            self.ctxu = data.get('_id')
            self.ctxc = data.get('default_company_id')
            self.auth_token = data.get('authentication_token')
            self.trusted_device = data.get('trusted_device')
            self.api_version = data.get('api_version')

            self.session.headers.update({
                'HB-Api-User-Id': self.ctxu,
                'HB-Api-Auth-Token': self.auth_token,
                'HB-Trusted-Device': self.trusted_device,
                'HB-Api-Client-Version': str(self.api_version)
            })
        except HTTPError as e:
            self.logger.error(f'Ошибка получение access token: {repr(e)}')
            raise AuthenticationError('Ошибка получение access token', e)

    def _mark_all_notifications_as_seen(self) -> None:
        """
        Помечает все уведомления как просмотренные
        """
        params = {
            'ctxu': self.ctxu,
            'ctxc': self.ctxc,
        }

        url = f'https://api.honeybook.com/api/v2/users/{self.ctxu}/mark_all_web_notifications_as_seen'

        try:
            response = self.session.put(url, params=params)
            response.raise_for_status()

            self.logger.info('Все уведомления помечены как прочитанные')
        except HTTPError as e:
            self.logger.error(f'Ошибка при помечении всех уведомлений как прочитаные: {repr(e)}')

    def get_all_notifications(self) -> list:
        """Возвращает все новые уведомления и помечает их как просмотренные"""
        params = {
            'ctxu': self.ctxu,
            'ctxc': self.ctxc,
        }
        notifications = []

        url = f'https://api.honeybook.com/api/v2/users/{self.ctxu}/web_notifications'

        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            is_unseen = data.get('has_unseen_notifications')
            if is_unseen:
                notifications = data.get('activity_notifications')

                for notification in notifications:
                    # if not notification.get('seen'):
                    notification_id = notification.get('data').get('opportunity_id')
                    if notification_id is None:
                        notification_id = notification.get('data').get('opportunity_ids')

                        if notification_id is None:
                            continue

                        notification_id = ','.join(notification_id)

                    notifications.append(notification_id)

                self._mark_all_notifications_as_seen()
        except Exception as e:
            self.logger.error('Ошибка получения списка уведомлений')
            self.logger.error(e)

        self.logger.info(f'Получено {len(notifications)} новых уведомлений')
        return notifications

    def get_client_info(self, client_id: str) -> list:
        """
        Возвращет данные о клиенте по его айди
        """
        clients_info = []

        if ',' in client_id:
            clients = self._get_client_info_by_ids(client_id)
        else:
            clients = self._get_client_info_by_id(client_id)

        for client in clients:
            time.sleep(5)
            info = {
                'source_id': client.get('_id'),
                'title': client.get('looking_for'),
                'price': set_budget(client.get('min_budget'), client.get('max_budget')),
                'location': client.get('location'),
                'tags': ','.join(client.get('vendor_types')),
                'description': client.get('description'),
                'name': client.get('creator').get('full_name'),
                'type': client.get('creator').get('user_type_name'),
                'phone': empty_str_to_none(get_phone_number(client.get('description'))),
                'email': empty_str_to_none(get_email(client.get('description'))),
                'website': client.get('creator').get('network').get('public_profile_url'),
                'time_published': datetime.strptime(client.get('created_at')
                                                    .replace('T', ' ').replace('Z', ''), '%Y-%m-%d %H:%M:%S.%f'),
            }
            info.update(self.get_client_profile_info(client.get('creator').get('_id')))
            clients_info.append(info)

        self.logger.debug(f'Получено данных из {len(client_id.split(","))} id')

        return clients_info

    def _get_client_info_by_id(self, client_id: str) -> list:
        """
        Возвращет json файл от сайта по айди клиента
        """
        params = {
            'ctxu': self.ctxu,
            'ctxc': self.ctxc,
            'all_opportunities': 'false',
            'lat': '40.6501038',
            'lng': '-73.9495823',
            'my_opportunities_only': 'true',
            'pinned_object_id': client_id,
        }

        url = f'https://api.honeybook.com/api/v2/network/user/{self.ctxu}/opportunities'

        response = self.session.get(url, params=params)
        try:
            response.raise_for_status()
            return [response.json().get('data')[0]]

        except HTTPError as e:
            self.logger.error(f'Ошибка при получении информации о клиенте: {repr(e)}')
            return []

    def _get_client_info_by_ids(self, client_ids: str) -> List:
        """
        Возвращет json файл из запроса по client_ids
        """
        params = {
            'ctxu': self.ctxu,
            'ctxc': self.ctxc,
            'opportunity_ids': client_ids,
        }
        url = 'https://api.honeybook.com/api/v2/network/opportunities'

        response = self.session.get(url, params=params)

        try:
            response.raise_for_status()
            return response.json().get('data')
        except HTTPError as e:
            self.logger.error(f'Ошибка при получении информации о клиентах: {repr(e)}')

        return []

    def get_client_profile_info(self, client_id: str) -> dict:
        """
        Возвращает контактную информацию клиента
        """
        params = {
            'ctxu': self.ctxu,
            'ctxc': self.ctxc,
        }
        url = f'https://api.honeybook.com/api/v2/network/user/{client_id}'

        response = self.session.get(url, params=params)

        try:
            response.raise_for_status()
        except Exception as e:
            self.logger.error('Ошибка при получении контактной информации клиента')
            self.logger.error(e)
        network = response.json()['network']

        return {
            "website": empty_str_to_none(network["website_url"]),
            "instagram": empty_str_to_none(network["instagram_url"]),
            "facebook": empty_str_to_none(network["facebook_url"]),
            "pinterest": empty_str_to_none(network["pinterest_url"]),
            "snapchat": empty_str_to_none(network["snapchat_url"]),
        }


def get_data_from_notif(client_api: HoneyBook) -> Optional[List]:
    notifications = client_api.get_all_notifications()
    client_information = [info for client in notifications for info in client_api.get_client_info(client)]
    client_api.logger.info(f'Из {len(notifications)} уведомлений получено '
                           f'{len(client_information)} данных о пользователях')

    return client_information

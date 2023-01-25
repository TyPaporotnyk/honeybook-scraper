from fake_useragent import UserAgent
from utils import *
from config import HONEYBOOK_EMAIL, HONEYBOOK_PASSWORD
from requests import Session
from datetime import datetime
import time

class HoneyBook(object):
    def __init__(self, logger = create_logger('HoneyBook')) -> None:
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
        self.setAccessToken()

    def setAccessToken(self) -> None:
        """Получает Access tokent и задает его в headeres"""
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
        except Exception as e:
            self.logger.error('Ошибка получение access токена')

    def markAllNotificationsAsSeen(self) -> None:
        """Помечает все уведомления как просмотренные"""
        params = {
            'ctxu': self.ctxu,
            'ctxc': self.ctxc,
        }

        url = f'https://api.honeybook.com/api/v2/users/{self.ctxu}/mark_all_web_notifications_as_seen'

        try:
            response = self.session.put(url, params=params)
            response.raise_for_status()

            self.logger.info('Все уведомления помечены как прочитанные')
        except Exception:
            self.logger.error('Ошибка при помечении всех уведомлений как прочитаные')

    def getAllNotifications(self) -> list:
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
            is_unsin = data.get('has_unseen_notifications')
            if is_unsin:
                notifs = data.get('activity_notifications')

                for notif in notifs:
                    # if not notif.get('seen'):
                    id = notif.get('data').get('opportunity_id')
                    if id is None:
                        id = notif.get('data').get('opportunity_ids')

                        if id is None:
                            continue

                        id = ','.join(id)

                    notifications.append(id)

                self.markAllNotificationsAsSeen()
        except Exception as e:
            self.logger.error('Ошибка получения списка уведомлений')
            self.logger.error(e)

        self.logger.info(f'Получено {len(notifications)} новых уведомлений')
        return notifications

    def getClientInfo(self, id: str) -> list:
        """Возвращет данные о клиенте по его айди"""
        clients = []
        clients_info = []

        if ',' in id:
            clients = self.getClientInfoByIds(id)
        else:
            clients = self.getClientInfoById(id)

        for client in clients:
            time.sleep(5)
            info = {
                'source_id': client.get('_id'),
                'title': client.get('looking_for'),
                'price': setBudget(client.get('min_budget'), client.get('max_budget')),
                'location': client.get('location'),
                'tags': ','.join(client.get('vendor_types')),
                'description': client.get('description'),
                'name': client.get('creator').get('full_name'),
                'type': client.get('creator').get('user_type_name'),
                'phone': empty_str_to_none(getPhoneNumberFromDescription(client.get('description'))),
                'email': empty_str_to_none(getEmailFromDescription(client.get('description'))),
                'website': client.get('creator').get('network').get('public_profile_url'),
                'time_published': datetime.strptime(client.get('created_at').replace('T', ' ').replace('Z', ''), '%Y-%m-%d %H:%M:%S.%f'),
            }
            info.update(self.getClientProfileInfo(client.get('creator').get('_id')))
            clients_info.append(info)

        self.logger.debug(f'Получено данных из {len(id.split(","))} id')

        return clients_info

    def getClientInfoById(self, client_id: str) -> list:
        """Возвращет json файл от сайта по айди клиента"""
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

        except Exception as e:
            self.logger.error('Ошибка при получении информации о клиенте')
            # self.logger.error(e)
            return []

    def getClientInfoByIds(self, client_ids: str) -> list:
        """Возвращет json файл от сайта по айди клиентов"""
        params = {
            'ctxu': self.ctxu,
            'ctxc': self.ctxc,
            'opportunity_ids': client_ids,
        }
        url = f'https://api.honeybook.com/api/v2/network/opportunities'

        response = self.session.get(url, params=params)

        try:
            response.raise_for_status()
            return response.json().get('data')
        except Exception as e:
            self.logger.error('Ошибка при получении информации о клиентах')
            # self.logger.error(e)

        return []

    def getClientProfileInfo(self, client_id: str) -> dict:
        """Возвращает контактную информацию клиента"""
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


def getDataFromNotif(client_api: HoneyBook) -> None:
    notifications = client_api.getAllNotifications()
    clientInforations = [info for client in notifications for info in client_api.getClientInfo(client)]
    client_api.logger.info(f'Из {len(notifications)} уведомлений получено {len(clientInforations)} данных о пользователях')

    return clientInforations
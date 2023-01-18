from prototypes.singleton import Singleton
import requests

@Singleton
class HoneyBook(object):
    ctxc = ''
    ctxu = ''
    auth_token = ''
    trusted_device = ''
    api_version = 0

    notifications = []

    def __init__(self):
        self.getAcces()

    def getAllNotifications(self):
        params = {
            'ctxu': self.ctxu,
            'ctxc': self.ctxc,
        }

        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6.1 Safari/605.1.15',
            'Host': 'api.honeybook.com',
            'Origin': 'https://www.honeybook.com',
            'Connection': 'keep-alive',
            'Accept-Language': 'ru',
            'Accept': 'application/json, text/plain, */*',
            'HB-Referer': 'https://www.honeybook.com/app/home',
            'HB-Api-User-Id': self.ctxu,
            'HB-Api-Auth-Token': self.auth_token,
            'HB-Trusted-Device': self.trusted_device,
            'HB-Api-Client-Version': '1936',
        }

        url = f'https://api.honeybook.com/api/v2/users/{self.ctxu}/web_notifications'

        response = requests.get(
            url,
            params=params,
            headers=headers
        )

        status_code = response.status_code

        if 200 < status_code > 204:
            print('[Error][Get notification] Status code is: ', status_code)
            return
        print('[Success][Get notification] Status code is: ', status_code)

        data = response.json()

        is_unsin = data.get('has_unseen_notifications')
        if is_unsin:
            notifs = data.get('activity_notifications')

            for notif in notifs:
                if not notif.get('seen'):
                    id = notif.get('data').get('opportunity_id')
                    if id is None:
                        id = notif.get('data').get('opportunity_ids')

                        if id is None:
                            continue

                        id = ','.join(id)

                    self.notifications.append({
                        'opportunity_id': id
                    })

            self.markAllNotificationsAsSeen()

    def markAllNotificationsAsSeen(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6.1 Safari/605.1.15',
            'Host': 'api.honeybook.com',
            'Origin': 'https://www.honeybook.com',
            'Connection': 'keep-alive',
            'Accept-Language': 'ru',
            'Accept': 'application/json, text/plain, */*',
            'HB-Referer': 'https://www.honeybook.com/app/home',
            'HB-Api-User-Id': self.ctxu,
            'HB-Api-Auth-Token': self.auth_token,
            'HB-Trusted-Device': self.trusted_device,
            'HB-Api-Client-Version': '1936',
        }

        params = {
            'ctxu': self.ctxu,
            'ctxc': self.ctxc,
        }

        url = f'https://api.honeybook.com/api/v2/users/{self.ctxu}/mark_all_web_notifications_as_seen'

        response = requests.put(
            url,
            headers=headers,
            params=params
        )

        status_code = response.status_code

        if 200 < status_code > 204:
            print('[Error][Mark all notofication] Status code is: ', status_code)
            return
        print('[Success][Mark all notofication] Status code is: ', status_code)
        print('[Success] All notofications marked as seen')

    def getAcces(self):
        json_data = {
            'password': 'Artlook199!',
            'trust_device': True,
            'source': 'link',
            'sourceData': {},
            'fingerprint': 'e633423f731453fc2a9dbfc711ef43b8',
        }

        response = requests.post(
            'https://api.honeybook.com/api/v2/users/info%40artlook.us/tokens',
            json=json_data,
        )

        status_code = response.status_code

        print()
        if 200 < status_code > 204:
            print('[Error][Get access] Status code is: ', status_code)
            return
        print('[Success][Get access] Status code is: ', status_code)
        print()

        data = response.json()
        self.ctxu = data.get('_id')
        self.ctxc = data.get('default_company_id')
        self.auth_token = data.get('authentication_token')
        self.trusted_device = data.get('trusted_device')
        self.api_version = data.get('api_version')
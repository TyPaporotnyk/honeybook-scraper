import scrapy
import json
from scraper.notifications.honeybook import HoneyBook
from datetime import datetime
import urllib

class NotificationSpider(scrapy.Spider):
    name = 'notif'

    def start_requests(self):
        for notif in HoneyBook.Instance().notifications:
            opportunity_id = notif.get('opportunity_id')

            headers = {
                'Host': 'api.honeybook.com',
                'Origin': 'https://www.honeybook.com',
                'Connection': 'keep-alive',
                'Accept-Language': 'ru',
                'Accept': 'application/json, text/plain, */*',
                'HB-Referer': '',
                'HB-Api-User-Id': HoneyBook.Instance().ctxu,
                'HB-Api-Auth-Token': HoneyBook.Instance().auth_token,
                'HB-Trusted-Device': HoneyBook.Instance().trusted_device,
                'HB-Api-Client-Version': str(HoneyBook.Instance().api_version),
            }

            if ',' in opportunity_id:
                url = f'https://api.honeybook.com/api/v2/network/opportunities?ctxu={HoneyBook.Instance().ctxu}&ctxc={HoneyBook.Instance().ctxc}&opportunity_ids={opportunity_id}'
                headers['HB-Referer'] = f'https://www.honeybook.com/app/community?opportunity_ids={opportunity_id}'

                yield scrapy.Request(
                    url,
                    headers=headers,
                    callback=self.parse_ids,
                )

            else:
                headers['HB-Referer'] = f'https://www.honeybook.com/app/community?opportunity_id={opportunity_id}'

                params = {
                    'ctxu': HoneyBook.Instance().ctxu,
                    'ctxc': HoneyBook.Instance().ctxc,
                    'all_opportunities': 'false',
                    'lat': '40.6501038',
                    'lng': '-73.9495823',
                    'my_opportunities_only': 'true',
                    'pinned_object_id': opportunity_id,
                }

                url = f'https://api.honeybook.com/api/v2/network/user/{HoneyBook.Instance().ctxu}/opportunities?{urllib.parse.urlencode(params)}'


                yield scrapy.Request(
                    url,
                    headers=headers,
                    callback=self.parse_id,
                )

    def parse_ids(self, response):
        datas = response.json().get('data')

        for data in datas:
            price = ''
            min_budget = data.get('min_budget')
            max_budget = data.get('max_budget')

            if max_budget is None and min_budget is None:
                price = None
            elif max_budget is None and min_budget is not None:
                price = f'{min_budget}$'
            elif max_budget is not None and min_budget is None:
                price = f'{max_budget}$'
            else:
                price = f'{min_budget}$ - {max_budget}$'

            yield {
                'source_id': data.get('_id'),
                'title': data.get('looking_for'),
                'price': price,
                'location': data.get('location'),
                'tags': ','.join(data.get('vendor_types')),
                'description': data.get('description'),
                'name': data.get('creator').get('full_name'),
                'type': data.get('creator').get('user_type_name'),
                'website': data.get('creator').get('network').get('public_profile_url'),
                'time_published': datetime.strptime(data.get('created_at').replace('T', ' ').replace('Z', ''), '%Y-%m-%d %H:%M:%S.%f'),
            }

    def parse_id(self, response):
        data = response.json().get('data')[0]

        price = ''
        min_budget = data.get('min_budget')
        max_budget = data.get('max_budget')

        if max_budget is None and min_budget is None:
            price = None
        elif max_budget is None and min_budget is not None:
            price = f'{min_budget}$'
        elif max_budget is not None and min_budget is None:
            price = f'{max_budget}$'
        else:
            price = f'{min_budget}$ - {max_budget}$'

        yield {
            'source_id': data.get('_id'),
            'title': data.get('looking_for'),
            'price': price,
            'location': data.get('location'),
            'tags': ','.join(data.get('vendor_types')),
            'description': data.get('description'),
            'name': data.get('creator').get('full_name'),
            'type': data.get('creator').get('user_type_name'),
            'website': data.get('creator').get('network').get('public_profile_url'),
            'time_published': datetime.strptime(data.get('created_at').replace('T', ' ').replace('Z', ''), '%Y-%m-%d %H:%M:%S.%f'),
        }
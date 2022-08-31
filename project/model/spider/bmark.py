import json
import time

import requests
from hashlib import md5

from project.config import BMARK_AUTH
from project.utils.logger import Log


class BMark:
    _REQUEST_BASE = 'https://bmark.cn'
    PLATFORM_ID = 9
    logger = Log('bmark')

    def get_all_collections(self):
        page = 0
        page_size = 10
        while True:
            page += 1
            self.logger.info(f'request page: {page}')
            fetch = requests.get(self._REQUEST_BASE + '/api/digitalCollectionSell/page',
                                 headers={'Authorization': 'Bearer ' + BMARK_AUTH},
                                 params={'current': page, 'size': page_size, 'sellType': 1, 'type': 1}).json()
            if fetch['code']:
                self.logger.error('failed to request: {}'.format(fetch))
                break
            feed = fetch['data']['records']
            if not feed:
                break
            for c in feed:
                c['collection_id_md5'] = md5(f'{self.PLATFORM_ID}-{c["digitalCollectionId"]}'
                                             f'-bmark'.encode('utf8')).hexdigest()
                c['edition_id_md5'] = md5(f"{self.PLATFORM_ID}-{c['editionNumber']}-bmark".encode('utf8')).hexdigest()
                yield c
            if len(feed) < page_size:
                break

    def get_sell_detail(self, sell_id):
        self.logger.info(f'request detail: {sell_id}')
        fetch = requests.get(self._REQUEST_BASE + f'/api/digitalCollectionSell/getDigitalCollectionInfo/{sell_id}',
                             headers={'Authorization': 'Bearer ' + BMARK_AUTH}).json()
        if fetch['code']:
            self.logger.error('failed to get sell detail: {}'.format(fetch))
            return None
        return fetch['data']

    def get_sale_record(self, asset_id):
        self.logger.info(f'request record for: {asset_id}')
        page = 0
        page_size = 10
        while True:
            page += 1
            self.logger.info(f'request record page: {page}')
            try:
                fetch = requests.get(self._REQUEST_BASE + '/api/userTransaction/tradePage',
                                     headers={'Authorization': 'Bearer ' + BMARK_AUTH},
                                     params={'current': page, 'size': page_size, 'assetsId': asset_id}).json()
            except json.JSONDecodeError:
                time.sleep(3)
                break
            if fetch['code']:
                self.logger.error('failed to fetch record: {}'.format(fetch))
                break
            records = fetch['data']['records']
            if not records:
                break
            for r in records:
                yield r
            if len(records) < page_size:
                break


if __name__ == '__main__':
    import pprint
    for co in BMark().get_all_collections():
        pprint.pp(co)
        break


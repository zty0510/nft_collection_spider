import json
import pprint
import time
from base64 import decodebytes, encodebytes

import requests
from Crypto.Cipher import AES

from project.utils.logger import Log


class Hi:
    PLATFORM_ID = 10
    logger = Log('hi')
    _REQUEST_BASE = 'https://szwc.juntu.com'
    _SECRET = '9af345D5juntu146'.encode('utf8')

    def fetch_all_collections(self):
        for tp in (1, 2):
            page = 0
            while True:
                page += 1
                self.logger.info(f'request page: {page}')
                resp = requests.get(self._REQUEST_BASE + '/api/api/product/listsType',
                                    params={'methodType': 1, 'request_data': self.encrypt(json.dumps({
                                        'page': page, 'limit': 7, 'type_id': tp, 'origin': 'h5',
                                        'timestamp': int(time.time())
                                    }))}).json()
                if not resp['code'] == 200:
                    self.logger.error(f'stop for good: {resp}')
                    break
                feed = json.loads(self.decrypt(resp['data']))['list']
                if not feed:
                    break
                for item in feed:
                    if item['is_serial'] == 'Y':
                        for p in self.list_serial_products(item['id']):
                            p['serial_info'] = item
                            yield p
                    else:
                        yield item

    def fetch_detail(self, cid):
        self.logger.info(f'fetching detail: {cid}')
        resp = requests.get(self._REQUEST_BASE + '/api/api/product/productInfo',
                            params={'methodType': 1, 'request_data': self.encrypt(json.dumps({
                                'id': str(cid), 'origin': 'h5', 'timestamp': int(time.time())
                            }))}).json()
        if not resp['code'] == 200:
            raise Exception('stop for good')
        return json.loads(self.decrypt(resp['data']))

    def list_serial_products(self, serial_no):
        page = 0
        while True:
            page += 1
            self.logger.info(f'request serial page: {page}')
            resp = requests.get(self._REQUEST_BASE + '/api/api/product/listsSerial',
                                params={'methodType': 1, 'request_data': self.encrypt(json.dumps({
                                    'page': page, 'limit': 6, 'serial_id': str(serial_no), 'origin': 'h5',
                                    'timestamp': int(time.time())
                                }))}).json()
            if not resp['code'] == 200:
                raise Exception('stop for good')
            feed = json.loads(self.decrypt(resp['data']))['list']
            if not feed:
                break
            for p in feed:
                yield p

    def encrypt(self, data):
        def padding(raw):
            raw = raw.encode('utf8')
            pad = AES.block_size - len(raw) % AES.block_size
            return raw + (chr(pad) * pad).encode('utf8')

        cipher = AES.new(self._SECRET, AES.MODE_ECB)
        return encodebytes(cipher.encrypt(padding(data)))

    def decrypt(self, data):
        def un_padding(raw):
            return raw[0:-ord(raw[len(raw)-1:])]
        cipher = AES.new(self._SECRET, AES.MODE_ECB)
        return un_padding(cipher.decrypt(decodebytes(data.encode('utf8'))).decode('utf8'))


if __name__ == '__main__':
    for c in Hi().fetch_all_collections():
        pprint.pp(c)
        break

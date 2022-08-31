import base64
import json
import pprint
import re
import time
import traceback

import requests
from threading import Lock
from urllib.parse import quote
from datetime import datetime
from base64 import decodebytes
from Crypto.Cipher import AES
from hashlib import md5

from project.config import ONE_ART_SECRET, ONE_ART_SIG, ONE_ART_AUTH, MAX_RETRY
from project.utils.logger import Log

_api_request_lock = Lock()


class OneArt:
    _REQUEST_BASE = 'http://r2.dsjcj.cc:10186'
    _TOKEN = "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAw3Jrw3I9yW6dVFN3XQcw"
    PLATFORM_ID = 1

    logger = Log('one-art')

    def __init__(self, authorize=ONE_ART_AUTH, signature=ONE_ART_SIG):
        self.authorize = authorize
        self.signature = signature

    # def get_sale_record_list(self, category):
    #     page = 0
    #     self.logger.info(f'fetching category: {category}')
    #     while True:
    #         page += 1
    #         self.logger.info(f'fetch page: {page}')
    #         resp = self.post('/open/api/saleRecord/list',
    #                          {'statusSale': '1', 'page': page,
    #                           'commodityCategoryIdList': [category]})
    #         if not resp:
    #             break
    #         for r in resp:
    #             yield r

    def get_activity_calendar(self):
        page = 0
        while True:
            page += 1
            self.logger.info(f'request page: {page}')
            resp = requests.post('https://api.theone.art/activity/api/activityCalendar/page',
                                 headers={'Content-Type': 'application/json;charset=UTF-8'},
                                 json={'pageIndex': page, 'pageSize': 9}).json()
            records = resp['data']['records']
            if not records:
                break
            for item in records:
                yield item


    def get_item_detail(self, item_id):
        self.logger.info(f'fetching for detail: {item_id}')
        try:
            resp = requests.post('https://api.theone.art/market/api/saleRecord/detail',
                                 headers={'authorization': self.authorize},
                                 json={'id': item_id}).json()
        except json.JSONDecodeError:
            time.sleep(3)
            return {}
        if not resp['code'] == 200:
            self.logger.error('failed to request')
            raise Exception('stop request for good')
        return resp['data']

    def get_collections_by_category(self, category, order=None, desc=False, max_page=0):
        page = 0
        if max_page:
            self.logger.info(f'max page: {max_page}')
        while True:
            page += 1
            self.logger.info(f'request page: {page}')
            args = {'pageCount': page, 'pageSize': 20, 'commodityCategoryId': category,
                    'statusSell': 1, 'sig': self.signature}
            if order:
                args['sort'] = {
                    'field': order,
                    'upOrDown': 1 if desc else 2
                }
            try:
                resp = requests.post('https://api.theone.art/market/api/saleRecord/list/v2',
                                     headers={'authorization': self.authorize, 'sig': quote(self.signature)},
                                     json=args).json()
            except json.JSONDecodeError:
                self.logger.error('json decode error')
                time.sleep(3)
                yield None
                return
            except:
                self.logger.error(traceback.format_exc())
                raise Exception('can not request')
            if not resp['code'] == 200:
                self.logger.error('failed to request')
                raise Exception('stop request for good')
            records = resp['data']['records']
            if not records:
                break
            for row in records:
                yield row
            if len(records) < 20 or (max_page and page > max_page):
                break

    def get_collection_prices(self, cid, max_pages=0):
        page = 0
        while True:
            page += 1
            self.logger.info(f'fetching price page: {page}')
            resp = self.post('/open/api/commodity/list', {'page': page, 'commodityId': cid})
            if not resp:
                break
            for c in resp:
                yield c
            if max_pages and page >= max_pages:
                break

    def get_all_categories(self, only_sub_market=False):
        categories = self.get('/open/api/commodityCategory/list')

        def extract_id(parent):
            r = []
            for p in parent:
                if p['childrens']:
                    r.extend(extract_id(p['childrens']))
                else:
                    r.append(p['id'])
            return r

        # pprint.pp([c for c in categories[0]['childrens'] if c['name'] == '衍生品市场'])
        if only_sub_market:
            return extract_id([c for c in categories[0]['childrens'] if c['name'] == '衍生品市场'])
        return extract_id(categories)

    # def get_collection_detail_by_api(self, cid):
    #     return self.post('/open/api/commodity/detail', {'commodityId': cid})

    def get_announcement(self, max_pages=5):
        page = 0
        while page < max_pages:
            page += 1
            self.logger.info(f'get announcement page: {page}')
            resp = self.post('/open/api/dynamicNews/list', {'page': page})
            if not resp:
                break
            for news in resp:
                news['time'] = datetime.strptime(news['time'], '%Y-%m-%d %H:%M').strftime('%Y-%m-%d %H:%M:%S')
                news['md5'] = md5(news['name'].encode('utf8')).hexdigest()
                news['platform'] = self.PLATFORM_ID
                yield news

    @staticmethod
    def encrypt(data, password=None, ret=None):
        if not password:
            password = ONE_ART_SECRET

        def padding(raw):
            raw = raw.encode('utf8')
            pad = AES.block_size - len(raw) % AES.block_size
            return raw + (chr(pad) * pad).encode('utf8')

        cipher = AES.new(decodebytes(password), AES.MODE_ECB)
        if not ret:
            return cipher.encrypt(padding(data)).hex()
        return base64.encodebytes(cipher.encrypt(padding(data))).decode('utf8').replace('\n', '')

    @staticmethod
    def decrypt(raw, password):
        def un_padding(r):
            r = r.decode('utf8')
            return r[:-ord(r[-1])]

        cipher = AES.new(base64.decodebytes(password.encode('utf8')), AES.MODE_ECB)
        return un_padding(cipher.decrypt(decodebytes(raw.encode('utf8'))))

    def get(self, path, _tried=0):
        if _tried > MAX_RETRY:
            raise Exception('max retry exceed!')
        try:
            with _api_request_lock:
                time.sleep(3)
                resp = requests.get(self._REQUEST_BASE + path, headers={'Open-Token': self._TOKEN}).json()
            if not resp['code'] == 200:
                time.sleep(3)
                self.logger.error(f'retry for code: {resp["code"]}')
                return self.get(path, _tried + 1)
            return resp['data']
        except:
            self.logger.error(traceback.format_exc())
            return self.get(path, _tried + 1)

    def post(self, path, data, _tried=0):
        if _tried > MAX_RETRY:
            raise Exception('max retry exceed!')
        try:
            with _api_request_lock:
                time.sleep(3)
                resp = requests.post(self._REQUEST_BASE + path, headers={'Open-Token': self._TOKEN},
                                     data={'param': self.encrypt(json.dumps(data))}).json()
            if not resp['code'] == 200:
                time.sleep(3)
                self.logger.error(f'retry for code: {resp["code"]}: {resp}')
                return self.post(path, data, _tried + 1)
            return resp.get('data', [])
        except:
            self.logger.error(traceback.format_exc())
            return self.post(path, data, _tried + 1)

    def fetch_all_artist(self):
        page = 0
        while True:
            page += 1
            self.logger.info(f'fetching artist page: {page}')
            resp = requests.post('https://api.theone.art/market/api/author/list',
                                 json={"pageCount": page, "pageSize": 20},
                                 headers={'authorization': self.authorize, 'sig': quote(self.signature)}
                                 ).json()['data']['records']
            if not resp:
                break
            for artist in resp:
                yield artist

    def fetch_artist_gallery(self, artist_id):
        page = 0
        self.logger.info(f'fetching gallery for: {artist_id}')
        while True:
            page += 1
            self.logger.info(f'fetching page: {page}')
            resp = requests.post('https://api.theone.art/goods/api/commodity/list',
                                 json={"authorId": artist_id, "pageSize": 16, "pageCount": page, "seriesWorksId": None},
                                 headers={'authorization': self.authorize,
                                          'sig': quote(self.signature)}).json()['data']['records']
            if not resp:
                break
            for collection in resp:
                yield collection

    def fetch_commodity_lowest_price(self, commodity_id, market_type, proxy=None):
        self.logger.info(f'fetching lowest price for: {commodity_id}')
        resp = requests.post('https://api.theone.art/market/api/saleRecord/list/v2',
                             headers={'authorization': self.authorize, 'sig': quote(self.signature)},
                             json={'commodityId': commodity_id, 'pageCount': 1, 'pageSize': 1,
                                   'statusSell': 1, 'sig': self.signature, 'typeMarket': market_type,
                                   'sort': {'field': 2, 'upOrDown': 1}}, proxies=proxy,
                             timeout=1).json()['data']['records']
        return resp[0]['price'] if resp else None

    # def fetch_all_sale_record(self, commodity_id, market_type):
    #     self.logger.info(f'fetching all sale record for: {commodity_id}')
    #     page = 0
    #     while True:
    #         page += 1
    #         resp = requests.post('https://api.theone.art/market/api/saleRecord/list/v2',
    #                              headers={'authorization': self.authorize, 'sig': quote(self.signature)},
    #                              json={'commodityId': commodity_id, 'pageCount': page, 'pageSize': 20,
    #                                    'statusSell': 1, 'sig': self.signature, 'typeMarket': market_type,
    #                                    'sort': {'field': 2, 'upOrDown': 1}}).json()['data']['records']
    #         if not resp:
    #             break
    #         for r in resp:
    #             yield r

    def get_signature(self):
        args_regs = re.compile(r"let (\w)=(\d*);")
        compiler_regs = re.compile(r"(result=.+?);")
        id_regs = re.compile(r'id=(.+?)}')
        self.logger.info('fetching signatures')
        # time.sleep(1)
        args = self.decrypt(requests.get('https://api.theone.art/market/api/key/get').json()['data'],
                            '5opkytHOggKj5utjZOgszg==')
        found_args = args_regs.findall(args)
        found_compiler = compiler_regs.findall(args)
        found_id = id_regs.findall(args)
        # print(args)
        env = dict([(k, int(v)) for k, v in found_args])
        exec(found_compiler[0], env)
        return self.encrypt(json.dumps({'id': found_id[0], 'sum': env['result']}),
                            '4tBlCLWFZ3eD93CvDE2lpw=='.encode('utf8'), 'base64')


if __name__ == '__main__':
    # print(len(OneArt('', '').get_all_categories()))
    for i in OneArt().get_activity_calendar():
        print(i)
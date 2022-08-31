import json
import time
from hashlib import md5

import requests

from project.utils.logger import Log
from project.config import TAOBAO_TOKEN


class XuMi:
    logger = Log('xu-mi')
    PLATFORM_ID = 6
    _REQUEST_BASE = 'https://h5api.m.taobao.com'
    _SHOP_ID = '12574478'

    def fetch_all_items(self):
        page = 0
        while True:
            page += 1
            args = json.dumps({'page': page, 'pageSize': 8, 'sellerId': 2213218033142})
            ts = int(time.time() * 1000)
            data_string = json.dumps({"dfApp": "paimai", "dfApiName": "paimai.new.org.auctionListFront",
                                      'dfVariables': args, 'dfVariablesRecover': args})
            resp = requests.get(self._REQUEST_BASE + '/h5/mtop.taobao.datafront.invoke/1.0/', params={
                'jsv': '2.4.2', 'appKey': self._SHOP_ID, 't': ts, 'api': 'mtop.taobao.datafront.invoke',
                'v': '1.0', 'type': 'jsonp', 'dataType': 'jsonp', 'callback': 'mtopjsonp1',
                'data': data_string, 'sign': self._digest(ts, data_string)
            }, headers={'Cookie': TAOBAO_TOKEN}).content.decode('utf8')
            feed = json.loads(resp[11:-1])['data']['GQL_auctions']['list']
            if not feed:
                break
            for item in feed:
                item['commodity_id'] = md5(f'{item["auctionBasic"]["title"]}-xumi'.encode('utf8')).hexdigest()
                item['item_id_hash'] = md5(f'{item["auctionBasic"]["itemId"]}-xumi'.encode('utf8')).hexdigest()
                yield item

    def fetch_item_detail(self, item_id):
        ts = int(time.time() * 1000)
        data_string = json.dumps({'itemId': str(item_id), 'scene': '', 'page': '1', 'pageSize': '3'})
        resp = requests.get(self._REQUEST_BASE + '/h5/mtop.taobao.auction.detail/1.0/',
                            headers={'Cookie': TAOBAO_TOKEN},
                            params={'jsv': '2.6.1', 'appKey': self._SHOP_ID, 't': ts, 'ttid': '1219@paimai_h5_1.0',
                                    'api': 'mtop.taobao.auction.detail', 'fullErrorResult': 'true', 'v': '1.0',
                                    'H5Request': 'true', 'type': 'jsonp', 'dataType': 'jsonp', 'callback': 'mtopjsonp1',
                                    'data': data_string, 'sign': self._digest(ts, data_string)}).content.decode('utf8')
        return json.loads(resp[11:-1])['data']

    @property
    def _secret_token(self):
        cookie_map = {}
        for k_v in TAOBAO_TOKEN.strip().split(';'):
            idx = k_v.index('=')
            cookie_map[k_v[0: idx].strip()] = k_v[idx+1:]
        return cookie_map['_m_h5_tk'].split('_')[0]

    def _digest(self, ts, data_string):
        return md5(f'{self._secret_token}&{ts}&{self._SHOP_ID}&{data_string}'.encode('utf8')).hexdigest()


if __name__ == '__main__':
    print(XuMi().fetch_item_detail(676846755894))

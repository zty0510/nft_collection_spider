import time
import requests
from hashlib import md5

from project.utils.logger import Log


class Qin:
    _REQUEST_BASE = 'https://api.nftqin.com'
    logger = Log('qin')
    PLATFORM_ID = 12
    _KEY = 'key=GuINI98Ct86qbhddazbTjoOAhGmyUNnP4AqVt2lp5NXk5mRTCfTW42QDYFJpKT7iCFoXL6GLnWb0wHKV9d7k3rhhy' \
           'Zh19oZgHxoGCslYLu8NkLulzwRuHk3X6AmfiiSi'

    def request(self, path, params):
        time.sleep(1)
        params['ts'] = int(time.time() * 1000)
        to_hash = ''.join(sorted([f'{k}={v}&' for k, v in params.items() if str(v)])) + self._KEY
        signature = md5(to_hash.encode('utf8')).hexdigest().upper()
        params['s'] = signature
        return requests.get(self._REQUEST_BASE + path, params=params).json()

    def get_all_collections(self):
        p = 0
        while True:
            p += 1
            resp = self.request('/api/public/goodsList', {'categroys': '-1', 'page': p, 'platform': 4})
            if resp['code'] != 200:
                self.logger.error(resp)
                break
            goods = resp['data']['data']
            if not goods:
                break
            for g in goods:
                g['cid_md5'] = md5(f"{g['id']}{self.PLATFORM_ID}-qin".encode('utf8')).hexdigest()
                g['gid_hash'] = '0' * 32
                yield g

    def get_collection_sale_records(self, cid):
        self.logger.info(f'request records for: {cid}')
        p = 0
        while True:
            p += 1
            self.logger.info(f'request page: {p}')
            resp = self.request('/api/public/marketplace',
                                {'sort': 2, 'sell_status': 1, 'page': p,
                                 'goods_id': cid, 'gd_type': 0, 'platform': 4})
            if resp['code'] != 200:
                self.logger.error(resp)
                break
            records = resp['data']['data']
            if not records:
                break
            for r in records:
                yield r


if __name__ == '__main__':
    Qin().get_collection_detail(126)


import pprint
from hashlib import md5

import requests

from project.utils.logger import Log


class Fifth:
    PLATFORM_ID = 18
    logger = Log('fifth')
    _REQUEST_BASE = 'https://nft.17kcps.com'

    def fetch_home_collections(self):
        page = 0
        while True:
            resp = requests.get(self._REQUEST_BASE + f'/app/app/version/list?pageNum={page}').json()
            records = resp['rows']
            if not records:
                break
            page += 1
            for r in records:
                if 'goodsList' in r:
                    for goods in r['goodsList']:
                        gid = goods['id']
                        goods['commodity_md5'] = md5(f'{gid}-fifth'.encode('utf8')).hexdigest()
                        yield goods, self.fetch_collection_detail(gid)
                else:
                    gid = r['id']
                    r['commodity_md5'] = md5(f'{gid}-fifth'.encode('utf8')).hexdigest()
                    yield r, self.fetch_collection_detail(gid)

    def fetch_collection_detail(self, i):
        return requests.get(self._REQUEST_BASE + f'/app/app/goods/{i}').json()

    def fetch_calendar(self):
        page = 0
        while True:
            resp = requests.get(self._REQUEST_BASE + f'/app/app/calendar/list?pageNum={page}').json()
            records = resp['rows']
            if not records:
                break
            page += 1
            for r in records:
                for goods in r['goodsList']:
                    gid = goods['id']
                    goods['commodity_md5'] = md5(f'{gid}-fifth'.encode('utf8')).hexdigest()
                    yield goods, self.fetch_collection_detail(gid)

    def fetch_before(self):
        page = 0
        while True:
            resp = requests.get(self._REQUEST_BASE + f'/app/app/before/list?pageNum={page}').json()
            records = resp['rows']
            if not records:
                break
            # pprint.pp(records)
            page += 1
            for goods in records:
                gid = goods['id']
                goods['commodity_md5'] = md5(f'{gid}-fifth'.encode('utf8')).hexdigest()
                yield goods, self.fetch_collection_detail(gid)


if __name__ == '__main__':
    for c in Fifth().fetch_home_collections():
        pprint.pp(c[1])
        break


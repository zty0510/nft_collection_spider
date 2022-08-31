import pprint

from hashlib import md5

import requests


class ShiCang:
    PLATFORM_ID = 14
    _REQUEST_BASE = 'https://collection.chinaso.com'

    def fetch_all_collections(self):
        page = 0
        while True:
            page += 1
            fetch = requests.post(self._REQUEST_BASE + '/collection-app/homepage/product/list_product',
                                  json={'pageNo': page, 'pageSize': 5}).json()
            products = fetch['data']['productList']
            if not products:
                break
            for p in products:
                p['hash_id'] = md5(f"{p['productCode']}-shicang".encode('utf8')).hexdigest()
                p['item_id'] = '0' * 32
                yield p


if __name__ == '__main__':
    for c in ShiCang().fetch_all_collections():
        pprint.pp(c)
        break


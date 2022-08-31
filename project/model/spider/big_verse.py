import pprint

import requests

from project.utils.logger import Log


class BigVerse:
    PLATFORM_ID = 21
    _REQUEST_BASE = 'https://api-pro.nftcn.com.cn'
    logger = Log('big-verse')

    def fetch_all_collections(self):
        for serial in self.fetch_all_serials():
            pprint.pp(serial)
            break

    def fetch_all_serials(self):
        page = 0
        while True:
            page += 1
            self.logger.info(f'request page: {page}')
            resp = requests.post(self._REQUEST_BASE + '/nms/dubbo/wanhuatong/appApi/explore/webSeries/list', json={
                'createSort': None, 'isExplore': 1, 'name': '', 'pageNum': page, 'pageSize': 20,
                'priceSort': None, 'sortBy': None
            }, headers={'Authorization': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJORlRDTl9DIiwiZXhwIjoxNjY0NzgxNjQ1LCJpYXQiOjE2NTcwMDU2NDUsImNvbnRlbnQiOiJ7XCJpZFwiOjE3MTgxMDl9In0.9hJH3jzD6PuTFyanekNd8L2zwnOIGK4x4XqPNFH5xCs'}).json()
            pprint.pp(resp)
            # ['result']['list']
            if not resp:
                break
            for s in resp:
                yield s


if __name__ == '__main__':
    BigVerse().fetch_all_collections()

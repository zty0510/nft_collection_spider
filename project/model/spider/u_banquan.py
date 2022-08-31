import pprint

import requests

from project.utils.logger import Log


class UBanQuan:
    PLATFORM_ID = 19
    _REQUEST_BASE = 'https://apimall.ubanquan.cn'
    logger = Log('u-ban-quan')

    def get_all_collections(self):
        page = 0
        while True:
            page += 1
            resp = requests.post(self._REQUEST_BASE + '/api/client-ubq-app/auctionMarket/pageAuctionProducts', headers={
                'url': 'main', 'os': 'Android', 'userDevice': 'HLK-AL00', 'appVersion': '2.0.5',
                'User-Agent': 'Ecopyright_Android/2.0.5', 'requestChannel': 'UBQ_ANDROID'
            }, json={'productFilterEnum': 'newest', 'pageSize': 10, 'terminal': 'ANDROID', 'sort': 'desc',
                     'pageNum': page, 'status': 1}).json()
            feed = resp.get('data')
            if not feed:
                break
            for item in feed:
                yield item

    def get_collection_detail(self, cid):
        resp = requests.get(self._REQUEST_BASE + f'/api/opactivity/discoverView/getAuctionDetailApp/{cid}', headers={
                'url': 'main', 'os': 'Android', 'userDevice': 'HLK-AL00', 'appVersion': '2.0.5',
                'User-Agent': 'Ecopyright_Android/2.0.5', 'requestChannel': 'UBQ_ANDROID'
            }).json()
        return resp.get('data')

    def fetch_all_themes(self):
        page = 0
        while True:
            page += 1
            self.logger.info(f'fetching store page: {page}')
            resp = requests.post(self._REQUEST_BASE + '/api/client-ubq-app/merchant/listV2', headers={
                'url': 'main', 'os': 'Android', 'userDevice': 'HLK-AL00', 'appVersion': '2.0.5',
                'User-Agent': 'Ecopyright_Android/2.0.5', 'requestChannel': 'UBQ_ANDROID'
            }, json={'pageSize': 30, 'pageNum': page}).json()['data']
            if not resp:
                break
            for store in resp:
                for theme in self.fetch_store_themes(store['storeNo']):
                    yield theme

    def fetch_store_themes(self, store_no):
        page = 0
        self.logger.info(f'fetching calendar for: {store_no}')
        while True:
            page += 1
            self.logger.info(f'fetching calendar for page: {page}')
            resp = requests.post(self._REQUEST_BASE + '/api/opactivity/client/theme/mobile/pageActivitiesV2', headers={
                'url': 'main', 'os': 'Android', 'userDevice': 'HLK-AL00', 'appVersion': '2.0.5',
                'User-Agent': 'Ecopyright_Android/2.0.5', 'requestChannel': 'UBQ_ANDROID'
            }, json={"storeNo": store_no, "isStop": 0, "pageSize": 30, "pageNum": page}).json()['data']
            if not resp:
                break
            for theme in resp:
                theme['detail'] = self.fetch_theme_detail(theme['themeKey'])
                yield theme

    @staticmethod
    def fetch_theme_detail(theme_key):
        return requests.post('https://static.ubanquan.cn/api/opactivity/client/theme/detail', headers={
                'url': 'main', 'os': 'Android', 'userDevice': 'HLK-AL00', 'appVersion': '2.0.5',
                'User-Agent': 'Ecopyright_Android/2.0.5', 'requestChannel': 'UBQ_ANDROID'
            }, json={"userId": "", "themeKey": theme_key}).json()['data']


if __name__ == '__main__':
    for i in UBanQuan().fetch_all_themes():
        pprint.pp(i)
        break


import json
import pprint
from hashlib import md5
import requests

from project.utils.logger import Log


class MgTV:
    PLATFORM_ID = 23
    logger = Log('mg-tv')

    def fetch_all_collections(self):
        page = 0
        while True:
            page += 1
            self.logger.info(f'request page: {page}')
            resp = requests.get('https://digital.bz.mgtv.com/publish/list', params={
                'pageNum': page, 'pageSize': 10, 'preview': 0, 'did': '729a0e4a-b5db-4730-8cb7-ab17a1fcbab1',
                'device': '', 'appVersion': '', 'osType': '', 'platform': 'android', 'abroad': 0,
                'src': '', 'uid': '', 'ticket': ''
            }).json()['data']['publishList']
            if not resp:
                break

            for c in resp:
                c['commodity_md5'] = md5(f'{c["publishId"]}-mg-tv'.encode('utf8')).hexdigest()
                yield c


if __name__ == '__main__':
    for _c in MgTV().fetch_all_collections():
        pprint.pp(_c)


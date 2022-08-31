import pprint

import requests

from project.utils.logger import Log


class JD_LingXi:
    PLATFORM_ID = 8
    logger = Log('jd-lx')
    _REQUEST_BASE = 'https://lxcp.jd.com'

    def get_all_collections(self):
        for serial in self.get_all_serials():
            if serial['goodsId']:
                yield serial, self.get_good_detail(serial['goodsId'])
                continue
            for c in self.get_serial_collections(serial['seriesId']):
                c['serial_info'] = serial
                yield c, self.get_good_detail(c['goodsId'])

    def get_all_serials(self):
        self.logger.info('fetching home serials')
        return requests.get(self._REQUEST_BASE +
                            '/gateway/mini/position/page?pageSize=9999').json()['data']['rows']

    def get_serial_collections(self, serial):
        self.logger.info(f'fetching serial collections for: {serial}')
        return requests.get(self._REQUEST_BASE + '/gateway/mini/series/get',
                            params={'seriesId': serial},
                            headers={'brain-access-token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ0ZW5hbnRUeXBlIjo5OSwiaWRlbnRpZmllciI6Im8qQUFTVnFXZ1I0YXNXOGJOd05EN2ItUlNTTURnek1YSG0xWEMzN090c2VjR2pnaFByamt1MUhMYWtKRGJ0Y29PZU4xUHZoSmdaIiwidXNlcklkIjoiMjgxNTM3NTUyNDMzMDk4NzUyIiwidGVuYW50TmFtZSI6Iua4uOWuouWMv-WQjeacuuaehCIsInRlbmFudElkIjoiMTcyNDYwNjQ3NDY1Mjc1MzkyIiwidXNlck5pY2tOYW1lIjoiamRfM3d1M0pBMkp5S2hzYklIIiwidXNlclR5cGUiOjk5LCJqZFBpbiI6ImpkXzN3dTNKQTJKeUtoc2JJSCIsInN0YXR1cyI6MSwianRpIjoiMjgxNTM3NTUyNDU0MDcwMjcyIiwiZXhwIjoxNjU3MTYxODIzfQ.bztxBTqcP9nH_BXA1Bl2DXTfhW1CKUSVrs_STGIoZEeAFM42cgvo21svrc42TYIZOG7kslXkdnQNARBmUUZxO586zMEUeqS9KZtHQiyy9QNqUtJ15qBw4HOkwcz94UftDo6Lc7VDLSwy1djJJnkcXL-4U8gz_UhT_Led40HFgF7r8n3AMaZOtYQbT1tCE8aHmC-ZIH1ueEu0pUMIJ8nRuHrvlfk6w_PhBSqZBfRiUXk7rKz7FHWQEqEgVzTNQa8pJ85tMiYDVadUhWYG_FUG8FMuEAikfV1Wp9JqYUjyUEWfsnHEshDBXhujH6eMG98M6rf34QNmOrJfhhxYeHRzdw',
                                     'brain-user-unique': 'b1cdb8f7b31e70af700f80ce0a655121ba288ec8'}
                            ).json()['data']['goods']

    def get_good_detail(self, gid):
        self.logger.info(f'fetching detail: {gid}')
        return requests.get(self._REQUEST_BASE + '/gateway/mini/goods/get',
                            params={'goodsId': gid}).json()['data']

    def get_all_announcement(self):
        return requests.get(self._REQUEST_BASE + '/gateway/mini/activity/list').json()['data']


if __name__ == '__main__':
    pprint.pp(JD_LingXi().get_all_announcement())
    # for i in JD_LingXi().get_all_collections():
    #     pprint.pp(i)
    #     break
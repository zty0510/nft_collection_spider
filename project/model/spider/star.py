import pprint
import requests
from hashlib import md5

from project.utils.logger import Log


class Star:
    PLATFORM_ID = 16
    logger = Log('star')
    _BASE_REQUEST = 'https://pgc.theuniquer.com'

    def fetch_all_collections(self):
        resp = requests.post(self._BASE_REQUEST +
                             '/saas/openapi/nftpgc/market/v1/queryWorksCategoryListByMerchantNumber').json()
        for category in resp['data']['worksCategoryList']:
            self.logger.info(f'fetching category: {category["categoryNumber"]}')
            series = requests.post(self._BASE_REQUEST +
                                   '/saas/openapi/nftpgc/market/v1/queryWorksSecondCategoryListByCategoryNumber',
                                   json={'categoryNumber': category['categoryNumber']}).json()
            for s in series['data']:
                sid = s['secondCategoryNumber']
                s.update(self.fetch_serial_detail(sid))
                for i in self.fetch_serial_items(sid):
                    i['serial_info'] = s
                    yield i

    def fetch_serial_detail(self, sid):
        resp = requests.post(self._BASE_REQUEST + '/saas/openapi/nftpgc/market/v1/querySerialDetail',
                             json={'secondCategoryNumber': sid}).json()
        return resp['data']

    def fetch_serial_items(self, sid):
        page = 0
        while True:
            page += 1
            resp = requests.post(self._BASE_REQUEST + '/saas/openapi/nftpgc/market/v1/querySaleNftWorksList',
                                 json={'curPageNo': page, 'secondCategoryNumber': sid, 'pageSize': 10}).json()
            feed = resp['data']['list']
            if not feed:
                break
            for item in feed:
                yield item

    def fetch_collection_detail(self, cid):
        self.logger.info(f'fetching collection: {cid}')
        resp = requests.post(self._BASE_REQUEST + '/saas/openapi/nftpgc/market/v1/queryNftWorksDetail', json={
            'worksNumber': cid
        }).json()
        return resp['data']

    def get_all_announcement(self):
        """
        might be a false
        :return:
        """
        page = 0
        while True:
            page += 1
            resp = requests.post('https://star.8.163.com/api/notice/v2/query', headers={
                'Cookie': 'NTES_YD_SESS=cpk3wyC7KDpwluViKwHpZSo15Ek0pQ0lL7BoHDFdVBDJ9dUy9SsiI2YP.bZm5e3Sz5vYpOm_ZQr7G6ZiRjtoZXHWCQpg6musMY7s0W3HgdEqV1j0WVlgy7QJkSrMDUbdty6_LjxxO4stwHuk6pD6LlWKCB7QR4Mxy7gy8k3D5m92w2ywAJAXSgR5y56bJ2i4cWxBzuofLKu1rhhvBvpAccxVNr6G9NdUehb63xQJm.0Qv; STAR_YD_SESS=cpk3wyC7KDpwluViKwHpZSo15Ek0pQ0lL7BoHDFdVBDJ9dUy9SsiI2YP.bZm5e3Sz5vYpOm_ZQr7G6ZiRjtoZXHWCQpg6musMY7s0W3HgdEqV1j0WVlgy7QJkSrMDUbdty6_LjxxO4stwHuk6pD6LlWKCB7QR4Mxy7gy8k3D5m92w2ywAJAXSgR5y56bJ2i4cWxBzuofLKu1rhhvBvpAccxVNr6G9NdUehb63xQJm.0Qv'
            }, json={"pageNum": page, "pageSize": 10}).json()['data']['announceList']
            if not resp:
                break
            for a in resp:
                a['md5'] = md5(f'{a["id"]}-wyxq'.encode('utf8')).hexdigest()
                yield a


if __name__ == '__main__':
    for i in Star().get_all_announcement():
        pprint.pp(i)
        break


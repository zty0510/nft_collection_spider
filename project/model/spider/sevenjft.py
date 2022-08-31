import base64
import hashlib
import json
import pprint
import time

import requests

from project.utils.logger import Log
from Crypto.Cipher import AES
from datetime import datetime

class SevenJFT:
    PLATFORM_ID = 26
    logger = Log('seven_jft')
    _SECRET = 'ljda_dj@.dv?sjdf'

    def __init__(self):
        self.type_name = self.get_keywords()

    def get_keywords(self):
        response = requests.get('https://v.7jft.com/api/index/keywords')
        decrypted_response = self.decrypt(response.json()['data'], self._SECRET)
        data = json.loads(decrypted_response)
        return data

    @staticmethod
    def decrypt(raw, password):
        def un_padding(r):
            r = r.decode('utf8')
            return r[:-ord(r[-1])]

        cipher = AES.new(password.encode('utf8'), AES.MODE_ECB)
        return un_padding(cipher.decrypt(base64.decodebytes(raw.encode('utf8'))))

    def search_works(self, work_name, page):
        t = time.time()
        params = {
            "name": work_name,
            "page": page,
            "pageSize":10,
            "sell_status": 0,
            "orders": "asc",
            "versionNum": "3.4.4",
            "opcodes": "T2gAI8B0bfN9PYlV7y7TyXh6gJVNDDJUvR1fv-VKPcfWv10pxSXYwFedkrENH6-6Gsw=",
            "tcode": int(t),
            "codeid": "428864a71572a65e49582151cca77881"
        }
        self.logger.info(f'requesting works')
        resp = requests.post('https://v.7jft.com/api/recommend/recommend/search_works',
                             headers={'Content-Type': 'application/json;charset=UTF-8','token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2NTkwNzk0MTcsInVpZCI6MjI4NjI5MiwidXNlcm5hbWUiOiJIUTE5MTk4ODY2MTMiLCJtb2JpbGUiOiIxNzMxNzUzMzE0NiIsInNhbHQiOiJDS1RHWmUifQ.Q0Obg-UIzoZM3uISTPHbfDMk24RWlSMAJ7XLNP2Bxp8'},
                             json=params).json()
        if not resp['code'] == 1:
            self.logger.error('failed to request works')
        return json.loads(self.decrypt(resp['data'], self._SECRET))

    def search_works_detail(self, work_id):
        params = {"id": work_id, "versionNum": "3.4.4", "tcode": int(time.time())}
        resp = requests.post('https://v.7jft.com/api/works/Likes/works_detail',
                             headers={
                                 'Content-Type': 'application/json;charset=UTF-8',
                                 'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2NTkwNzk0MTcsInVpZCI6MjI4NjI5MiwidXNlcm5hbWUiOiJIUTE5MTk4ODY2MTMiLCJtb2JpbGUiOiIxNzMxNzUzMzE0NiIsInNhbHQiOiJDS1RHWmUifQ.Q0Obg-UIzoZM3uISTPHbfDMk24RWlSMAJ7XLNP2Bxp8',
                                 'Cookie': 'SERVERID=22ca33cc8165cb494a38c2288aa1a089|1658733305|1658729024'},
                             json=params).json()
        if not resp['code'] == 1:
            self.logger.error('failed to request works_detail')
        return json.loads(self.decrypt(resp['data'], self._SECRET))


    def search_all_work(self):
        if not self.type_name:
            raise "type_name is None"
        for name in self.type_name:
            hl = hashlib.md5(("七级宇宙" + name).encode('utf8'))
            commodity_id = hl.hexdigest()
            page = 1
            while True:
                try:
                    data = self.search_works(name, page)['data']
                except Exception:
                    continue
                else:
                    page += 1
                    for item in data:
                        item_id = item['id']
                        detail = self.search_works_detail(item_id)
                        ht = hashlib.md5(str(item_id).encode('utf8'))
                        item_id = ht.hexdigest()
                        yield commodity_id, item_id, self.PLATFORM_ID, item, detail

    def get_news_info(self, news_id):
        params = {
            "versionNum": "3.4.4",
            "tcode": 1658741053,
            "id": news_id

        }
        resp = requests.post('https://v.7jft.com/api/news/newsInfo',
                             headers={
                                 'Content-Type': 'application/json;charset=UTF-8'},
                             json=params).json()
        data = resp['data']
        if not data:
            return None
        data = json.loads(self.decrypt(resp['data'], self._SECRET))
        return data['content']




    def get_all_announcement(self):
        page = 1
        while True:
            params={
                "page": page,
                "pageSize": 10,
                "versionNum": "3.4.4",
                "tcode": 1658741053
            }
            resp = requests.post('https://v.7jft.com/api/news/newsList',
                                 headers={
                                     'Content-Type': 'application/json;charset=UTF-8'},
                                 json=params).json()
            data = resp['data']
            if not data:
                break
            page += 1
            data = json.loads(self.decrypt(resp['data'], self._SECRET))
            for item in data:
                yield {'title': item['title'], 'cover': item['fmimg'],
                       'time': str(datetime.fromtimestamp(item['ctime'])),
                       'md5': item['id'], 'content': self.get_news_info(item['id'])
                       }


if __name__ == "__main__":
    a = SevenJFT()
    # pprint.pp(a.search_works('泰山', 1))
    # pprint.pp(i for i in a.search_all_work())
    for i in a.get_all_announcement():
        pprint.pp(i)
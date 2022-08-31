import datetime
import hashlib
import json
import pprint
import time

import requests

from project.utils.logger import Log


class YouWu:
    PLATFORM_ID = 37
    logger = Log('YouWu')

    def __init__(self):
        self.sess = requests.session()
        self.cookie_dict = self.get_cookie()

    def generate_sign(self, pageNo):
        token = self.cookie_dict['_m_h5_tk'][:32]
        app_key = '24679788'
        t = int(round(time.time() * 1000))
        params = {
            "bizCode": "YOU_WU",
            "pageNo": pageNo,
            "pageSize": 20
        }
        data = '{"name":"product_recommend","params":' + json.dumps(json.dumps(params, separators=(',', ':'))) + '}'
        # data = '{"name":"product_recommend","params":"{\\"bizCode\\":\\"YOU_WU\\",\\"pageNo\\":1,\\"pageSize\\":20}"}'

        origin = token + "&" + str(t) + "&" + app_key + "&" + data
        sign = hashlib.md5(origin.encode('utf8')).hexdigest()
        # print(data)
        return t, sign, data

    def get_cookie(self):
        # sign_set = self.generate_sign(page_no)
        # url = 'https://acs.youku.com/h5/mtop.youku.ykg.client.graphql.open/1.0/?appKey=24679788&t={time}&sign={sign}&data={data}'.format(
        #     time=sign_set[0], sign=sign_set[1], data=sign_set[2])
        url = 'https://acs.youku.com/h5/mtop.youku.ykg.client.graphql.open/1.0/?appKey=24679788'
        resp = self.sess.get(url)
        return resp.cookies.get_dict()

    def get_list(self):
        page_no = 1
        while True:
            sign_set = self.generate_sign(page_no)
            url = "https://acs.youku.com/h5/mtop.youku.ykg.client.graphql.open/1.0/?appKey=24679788&t={0}&sign={1}&data={2}".format(
                sign_set[0], sign_set[1], sign_set[2])
            resp = self.sess.get(url)
            # print(resp.json())
            try:
                products_list = resp.json()['data']['result']['products']
            except KeyError:
                print('fetching products failed, maybe page_no is oversize')
                break
            else:
                for item in products_list:
                    com_name = item['detail']['mainTitle']
                    commodity_id = hashlib.md5(("鱿物" + com_name).encode('utf8')).hexdigest()
                    yield {
                        'commodity_id': commodity_id,
                        'item_id': '0' * 32,
                        'collection': item,
                        'item_detail': None
                    }

            page_no += 1
if __name__ == "__main__":
    for i in YouWu().get_list():
        print(i)
        break
    # print(YouWu().generate_sign(1))
    # print()

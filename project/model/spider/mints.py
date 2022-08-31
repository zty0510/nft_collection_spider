import hashlib
import pprint

import requests

from project.utils.logger import Log


class MINTS:
    PLATFORM_ID = 36
    logger = Log('mints')

    def get_opus_list(self, package_id):
        offset = 0
        while True:
            params = {
                'id': package_id,
                'offset': offset,
                'limit': 100
            }
            self.logger.info('requesting opus list')
            resp = requests.post('https://go.mintstech.cn/packconfig/opus/list',
                                 json=params).json()
            data = resp['data']['opuslist']
            if not data:
                return
            yield data
            offset += 100



    def get_all_list(self):
        offset = 0
        while True:
            params = {
                'offset': offset,
                'limit': 100,
                'status': 0      # 0 all   3 sell  4 sold out
            }
            self.logger.info('requesting box list')
            resp = requests.post('https://go.mintstech.cn/activity/packconfig/list',
                                 json=params).json()
            package_list = resp['data']['packconfig']
            if not package_list:
                return None
            for box in package_list:
                package_id = box['id']
                hl = hashlib.md5((("mints" + str(package_id))).encode('utf8'))
                commodity_id = hl.hexdigest()
                # opus_list = self.get_opus_list(package_id)
                # for list in opus_list:
                    # for item in list:
                        # ht = hashlib.md5(("mints"+str(item['id'])).encode('utf8'))
                yield {
                    'commodity_id': commodity_id,
                    'item_id': '0' * 32,
                    'collection': box,
                    'item_detail': None
                }
            offset += 100
    def get_all_announcement(self):
        offset = 0
        while True:
            params = {
                'offset': offset,
                'limit': 100
            }
            resp = requests.post('https://go.mintstech.cn/article/list',
                                 json=params).json()
            news_list = resp['data']['list']
            if not news_list:
                return
            for news in news_list:
                cover_url = "https://cdn.mintstech.cn/images/" + news['coverImgWeb']
                news_id = hashlib.md5((news['title'] + str(news['id'])).encode('utf8')).hexdigest()
                ct = news['created']
                news_time = ct[0:10] + ' ' + ct[11:19]
                yield {'title': news['title'],'cover': cover_url, 'time': news_time,
                       'md5': news_id, 'content': news['content']}
            offset += 100

if __name__ == "__main__":
    t = 0
    for i in MINTS().get_all_list():
        print(i)
import pprint
import re
from hashlib import md5
import requests

from project.utils.logger import Log


class BiliBili:
    PLATFORM_ID = 24
    _REQUEST_BASE = 'https://api.bilibili.com'
    logger = Log('bilibili')
    lottery_id_regs = re.compile(r"lotteryId=(\d*)&")

    def fetch_all_collections(self):
        self.logger.info('fetching tab info')
        resp = requests.get(self._REQUEST_BASE + '/x/garb/v2/mall/home/calendar?tab=2').json()
        for year_data in resp['data']['list']:
            for month_item in year_data['list']:
                for item in month_item['list']:
                    lottery = self.lottery_id_regs.findall(item['jump_url'])
                    if not lottery:
                        continue
                    item['commodity_id'] = md5(f'{item["item_name"]}-bilibili'.encode('utf8')).hexdigest()
                    yield item, self.fetch_collection_detail(lottery[0])

    def fetch_collection_detail(self, lottery_id):
        self.logger.info('fetch brief info')
        resp = requests.get(self._REQUEST_BASE + f'/x/garb/activity/mall/lottery/detail?lottery_no={lottery_id}').json()
        raw = resp['data']
        item_id = raw['properties']['sale_item_id']
        self.logger.info('fetch detail info')
        detail = requests.get(self._REQUEST_BASE + f'/x/garb/v2/mall/digital/item/detail?item_id={item_id}&'
                                                   f'part=profile').json()['data']['item']
        raw['detail'] = detail
        return raw


if __name__ == '__main__':
    for i in BiliBili().fetch_all_collections():
        print(i)

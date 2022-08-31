# 小红书
import requests
from hashlib import md5

from project.utils.logger import Log


class RSpace:
    PLATFORM_ID = 17
    logger = Log('r-space')
    _REQUEST_BASE = 'https://www.xiaohongshu.com'

    def fetch_all_collections(self):
        cursor_id = 0
        size = 20
        while True:
            self.logger.info(f'fetching cursor: {cursor_id} size: {size}')
            resp = requests.get(self._REQUEST_BASE +
                                f"/api/themet/center/feed?cursor_id={cursor_id}&size={size}").json()['data']
            if 'cursor' not in resp:
                break
            cursor = resp['cursor']
            cursor_id = cursor['cursor_id']
            size = cursor['size']
            records = resp['items']
            if not records:
                break
            for r in records:
                r['commodity_id'] = md5(f"{r['item_id']}-r-space".encode('utf8')).hexdigest()
                yield r

    def fetch_calendars(self):
        resp = [c for c in requests.get(self._REQUEST_BASE + '/api/themet/center/cards').json()['data']['cards']
                if c['card_type'] == 1]
        return resp


if __name__ == '__main__':
    print(RSpace().fetch_calendars())


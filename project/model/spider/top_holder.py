import json
import pprint
from hashlib import md5
import requests

from project.utils.logger import Log


class TopHolder:
    PLATFORM_ID = 29
    logger = Log('top-holder')

    def fetch_all_collections(self):
        page = 0
        while True:
            page += 1
            self.logger.info(f'request page: {page}')
            resp = requests.get('https://www.topholder.cn/api/v1/frontend/nft/list',
                                params={'isAuction': 1, 'limit': 4, 'page': page}).json()['data']['list']
            if not resp:
                break
            for row in resp:
                detail = self.fetch_collection_detail(row['bid'])
                if not detail:
                    continue
                row['commodity_md5'] = md5(f'{row["id"]}-top-holder'.encode('utf8')).hexdigest()
                yield row, detail

    @staticmethod
    def fetch_collection_detail(cid):
        resp = requests.get('https://weibo-proxy.topholder.cn/statuses/show', params={'id': cid})
        if not resp.ok:
            return None
        try:
            return resp.json().get('data')
        except json.JSONDecodeError:
            return None


if __name__ == '__main__':
    for i in TopHolder().fetch_all_collections():
        pprint.pp(i)
        break

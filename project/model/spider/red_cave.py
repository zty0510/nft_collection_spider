import pprint

import requests
from hashlib import md5

from project.utils.logger import Log


class RedCave:
    logger = Log('red-cave')
    PLATFORM_ID = 13
    _REQUEST_BASE = 'https://redcave.com'

    def fetch_all_collections(self):
        page = 0
        while True:
            page += 1
            self.logger.info(f'request page: {page}')
            fetch = requests.post(self._REQUEST_BASE + '/api/casting/nftseries/findAll',
                                  data={'page': page, 'pageSize': 4}).json()
            feed = fetch['obj']
            if not feed:
                break
            for obj in feed:
                obj['hash_id'] = md5(f"{obj['id']}-red-cave".encode('utf8')).hexdigest()
                obj['item_id'] = '0' * 32
                yield obj


if __name__ == '__main__':
    for c in RedCave().fetch_all_collections():
        pprint.pprint(c)
        break


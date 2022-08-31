import pprint

import requests

from project.utils.logger import Log


class XinHua:
    PLATFORM_ID = 38
    logger = Log('xinhua')
    _REQUEST_BASE = 'https://my-api.app.xinhuanet.com'

    def fetch_all_collections(self):
        self.logger.info('fetching full collections')
        resp = requests.post(self._REQUEST_BASE + '/newnft/shucang/shucangList').json()
        return resp['data']


if __name__ == '__main__':
    pprint.pp(XinHua().fetch_all_collections())


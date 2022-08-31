import json
import pprint
import re

import requests
from hashlib import md5
from urllib.parse import unquote


class BBYZ:
    PLATFORM_ID = 39
    _page_data_regs = re.compile(r"window\._global = (.+?)\n")

    def get_all_collections(self):
        fetch = requests.get('https://shop106428992.m.youzan.com/v2/showcase/homepage?alias=Sgc8Wh3Npl&is_silence_auth=1').content.decode('utf8')
        for c in json.loads(unquote(json.loads(self._page_data_regs.findall(fetch)[0])['feature_components'])):
            if 'sub_entry' not in c:
                continue
            detail_url = c['sub_entry'][0]['link_url']
            if not detail_url:
                continue
            detail = self.extract_page_data(detail_url)
            detail['commodity_id'] = md5(f'{detail_url}-bbyz'.encode('utf8')).hexdigest()
            yield detail

    def extract_page_data(self, page):
        fetch = requests.get(page).content.decode('utf8')
        return json.loads(self._page_data_regs.findall(fetch)[0])


if __name__ == '__main__':
    for i in BBYZ().get_all_collections():
        pprint.pp(i)

import re
import pprint
from hashlib import md5

import requests
from bs4 import BeautifulSoup

from project.utils.logger import Log


class LingJing:
    PLATFORM_ID = 30
    logger = Log('lingjing')
    collection_name_regs = re.compile('《(.+?)》')

    def fetch_all_collections(self):
        self.logger.info('fetching home page')
        soup = BeautifulSoup(requests.get('http://art.people.com.cn/').content.decode('gbk'), 'html.parser')
        for author in soup.find('div', {'class': 'swiper-container swiper-container-p5'}).find_all('div', {'class': 'swiper-slide-con'}):
            author_line = author.find('a')
            author_url = author_line['href']
            author_name = author_line.find('img')['alt']
            for img, name in self.get_author_all_collections(self.fetch_author_base(author_url)):
                yield {
                    'author': author_name,
                    'image': img,
                    'name': name,
                    'id': md5(f'{img}-lj'.encode('utf8')).hexdigest()
                }

    def fetch_author_base(self, author_url):
        self.logger.info(f'fetching base for: {author_url}')
        soup = BeautifulSoup(requests.get(author_url).content.decode('gbk'), 'html.parser')
        collection_eg = soup.find('div', {'class': 'w1200 yl-d2p1 clearfix'}).find('a')['href']
        return collection_eg[:collection_eg.rindex('-')]

    def get_author_all_collections(self, base_url):
        page = 0
        while True:
            page += 1
            if page == 1:
                url = f'{base_url}.html'
            else:
                url = f'{base_url}-{page}.html'
            self.logger.info(f'fetching collection: {url}')
            resp = requests.get(url)
            if not resp.ok:
                break
            soup = BeautifulSoup(resp.content.decode('gbk'), 'html.parser')
            content = soup.find('div', {'class': 'lypic rm_txt cf'})
            pic = content.find('div', {'class': 'pic_data clearfix'}).find('img')
            name = self.collection_name_regs.findall(pic['alt'])
            yield 'http://art.people.com.cn' + pic['src'], name[0] if name else name


if __name__ == '__main__':
    LingJing().fetch_all_collections()

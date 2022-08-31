import pprint
from hashlib import md5

import requests
from bs4 import BeautifulSoup


class HBSC:
    PLATFORM_ID = 25
    _REQUEST_BASE = 'https://hb.dzwww.com'

    def get_all_announcement(self):
        soup = BeautifulSoup(requests.get(self._REQUEST_BASE + '/s/7875.html').content.decode('utf8'), 'html.parser')
        for li in soup.find('ul', {'id': 'list_23487'}).find_all('li'):
            cover_line = li.find('a', {'class': 'pic1'})
            article_link = cover_line['href']
            cover_link = cover_line.find('img')['src']
            title = li.find('h3').get_text()
            yield {'title': title, 'cover': cover_link, 'time': li.find_all('span')[-1].get_text() + ':00',
                   'content': self.get_article_detail(article_link),
                   'md5': md5(f'{title}-hbsc'.encode('utf8')).hexdigest()}

    def get_article_detail(self, article_link):
        soup = BeautifulSoup(requests.get(article_link).content.decode('utf8'), 'html.parser')
        return str(soup.find('div', {'class': 'news-body'}))[24:-6]


if __name__ == '__main__':
    for i in HBSC().get_all_announcement():
        pprint.pp(i)
        break



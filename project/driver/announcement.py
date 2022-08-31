
from datetime import datetime

from project.model.spider.mints import MINTS
from project.model.spider.sevenjft import SevenJFT
from project.utils.logger import Log
from project.model.announcement import Announcement
from project.model.spider.one_art import OneArt
from project.model.spider.star import Star
from project.model.spider.hbsc import HBSC


class Driver:
    logger = Log('announcement')
    announcement = Announcement()

    def sync(self, max_pages=5):
        for news in OneArt().get_announcement(max_pages):
            self.announcement.save_news(news['name'], news['cover'], news['time'], news['platform'], news['md5'],
                                        news['content'])

    def hbsc(self):
        api = HBSC()
        for news in api.get_all_announcement():
            self.announcement.save_news(news['title'], news['cover'], news['time'], api.PLATFORM_ID,
                                        news['md5'], news['content'])

    def star(self):
        api = Star()
        for news in api.get_all_announcement():
            news_md5 = news['md5']
            self.announcement.save_news(news['title'], '', str(datetime.fromtimestamp(news['startTime'] / 1000)),
                                        api.PLATFORM_ID, news_md5, news['content'])

    def seven_jft(self):
        api = SevenJFT()
        for news in api.get_all_announcement():
            self.announcement.save_news(news['title'], news['cover'], news['time'], api.PLATFORM_ID,
                                        news['md5'], news['content'])

    def mints(self):
        api = MINTS()
        for news in api.get_all_announcement():
            self.announcement.save_news(news['title'], news['cover'], news['time'], api.PLATFORM_ID,
                                        news['md5'], news['content'])

    # def jd_lx(self):
    #     api = JD_LingXi()
    #     announcement = Announcement()
    #     for news in api.get_all_announcement():
    #         name = news["activityName"]
    #         self.logger.info(f'saving: {name}')
    #
    #         announcement.save_news(news['activityName'], news['activityImg'], news['startTime'], api.PLATFORM_ID,
    #                                md5(f'{name}-jdlx'.encode('utf8')).hexdigest(), news['activityUrl'])

if __name__ == '__main__':
    Driver().mints()


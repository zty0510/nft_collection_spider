import json

from project.model.activity_calendar import ActivityCalendar
from project.model.spider.one_art import OneArt
from project.utils.logger import Log
from project.model.spider.u_banquan import UBanQuan
from project.model.spider.r_space import RSpace

from project.model.calendar import Calendar
from project.utils.time_helper import timestamp_2_date_int


class Driver:
    logger = Log('calendar')
    calendar = Calendar()

    def ubq(self):
        api = UBanQuan()
        batch = []
        for theme in api.fetch_all_themes():
            batch.append((api.PLATFORM_ID, theme['themeName'], 1,
                          'https://obs.prod.ubanquan.cn/' + theme['headImg'],
                          timestamp_2_date_int(theme['startTime'] / 1000), theme['detail']['price']))
            if len(batch) >= 20:
                self.calendar.save_calendars(batch)
                batch = []
        if batch:
            self.calendar.save_calendars(batch)

    def r_space(self):
        api = RSpace()
        for card in api.fetch_calendars():
            info = card['product_info']
            nft = card['nft_info']
            self.calendar.save_calendars([(api.PLATFORM_ID, card['name'], nft['count'], card['cover'],
                                           timestamp_2_date_int(info['sale_time']/1000),
                                           int(float(info['price']) * 100))])
    def one_art(self):
        api = OneArt()
        activity_calendar_model = ActivityCalendar()
        for item in api.get_activity_calendar():
            uuid = item['uuid']
            # pprint(item)
            activity_calendar_model.save_activity((uuid, json.dumps(item, ensure_ascii=False)))


if __name__ == '__main__':
    Driver.one_art()


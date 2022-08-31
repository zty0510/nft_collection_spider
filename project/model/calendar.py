
from functools import reduce

from project.config import MYSQL_CONFIG
from project.utils.logger import Log
from project.utils.mysql_helper import Mysql


class Calendar:
    logger = Log('calendar')
    table = 'calendar_raw'
    mysql = Mysql(MYSQL_CONFIG)

    def save_calendars(self, batch):
        self.logger.info(f'saving {len(batch)}')
        self.mysql.write(f'replace into {self.table} (platform, name, num, pic, date, price) values '
                         f'{",".join(["(%s,%s,%s,%s,%s,%s)"]*len(batch))}',
                         reduce(lambda a, b: a + b, batch))

    def read_all(self):
        return self.mysql.read_many(f'select platform, name, num, pic, date, price from {self.table}')




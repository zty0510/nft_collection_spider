
from project.config import MYSQL_CONFIG
from project.utils.logger import Log
from project.utils.mysql_helper import Mysql


class ActivityCalendar:
    logger = Log('activity_calendar')
    table = 'one_art_calendar'
    mysql = Mysql(MYSQL_CONFIG)

    def save_activity(self, data):
        self.logger.info('saving activity calendar now')
        self.mysql.write(f'replace into {self.table} (id, content) values (%s,%s)', data)


if __name__ == "__main__":
    pass


import json
from functools import reduce

from project.utils.logger import Log
from project.utils.mysql_helper import Mysql
from project.config import MYSQL_CONFIG


class TheOneLatestPublish:
    logger = Log('the-one-latest')
    mysql = Mysql(MYSQL_CONFIG)
    table = 'oneart_latest_publish'

    def save_record(self, cid, gid, record):
        self.logger.info(f'saving goods: {gid}')
        self.mysql.write(f'replace into {self.table} (cid, gid, publish) values (%s, %s, %s)',
                         (cid, gid, json.dumps(record, ensure_ascii=False)))

    def save_batch(self, batch):
        self.logger.info(f'saving: {len(batch)}')
        self.mysql.write(f'replace into {self.table} (record_ts, cid, gid, publish) values '
                         f'{",".join(["(%s, %s, %s, %s)"] * len(batch))}',
                         reduce(lambda a, b: a + b, batch))


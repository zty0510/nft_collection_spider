import json

from project.utils.logger import Log
from project.utils.mysql_helper import Mysql
from project.config import MYSQL_CONFIG


class Price:
    mysql = Mysql(MYSQL_CONFIG)
    table_raw = 'prices_raw'
    logger = Log('prices')

    def save_prices(self, platform, cid, prices):
        self.mysql.write(f'replace into {self.table_raw} (platform, commodity_id, prices) values (%s, %s, %s)',
                         (platform, cid, json.dumps(prices, ensure_ascii=False)))

    def read_all_commodities(self):
        return self.mysql.read_many(f'select platform, commodity_id from {self.table_raw}')

    def read_raw_prices(self, platform, cid):
        match = self.mysql.read_one(f'select prices from {self.table_raw} where '
                                    f'platform = %s and commodity_id = %s', (platform, cid))
        return json.loads(match[0]) if match else None

    def read_all_commodity_by_platform(self, platform):
        fetch = self.mysql.read_many(f'select commodity_id from {self.table_raw} where '
                                     f'platform = {int(platform)}')
        return [f for f, in fetch]


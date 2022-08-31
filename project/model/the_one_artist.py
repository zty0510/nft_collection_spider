
import json
from functools import reduce

from project.utils.logger import Log
from project.utils.mysql_helper import Mysql
from project.config import MYSQL_CONFIG


class TheOneArtist:
    logger = Log('the-one-artiest')
    mysql = Mysql(MYSQL_CONFIG)
    table_artist = 'one_art_artists'
    table_artist_collection = 'one_art_artist_gallery'
    table_cheapest_price = 'one_art_cheapest_price'

    def save_artist(self, aid, artist):
        self.logger.info(f'saving artist: {aid}')
        self.mysql.write(f'replace into {self.table_artist} (id, raw_info) values (%s, %s)',
                         (aid, json.dumps(artist, ensure_ascii=False)))

    def save_gallery(self, artist, cid, collection):
        self.mysql.write(f'replace into {self.table_artist_collection} (artist, cid, collection) values (%s, %s, %s)',
                         (artist, cid, json.dumps(collection, ensure_ascii=False)))

    def batch_save_lowest_price(self, batch):
        self.logger.info(f'saving lowest price batch: {len(batch)}')
        self.mysql.write(f'replace into {self.table_cheapest_price} (record_ts, cid, price) values '
                         f'{",".join(["(%s,%s,%s)"] * len(batch))}', reduce(lambda a, b: a + b, batch))

    def fetch_all_collections(self):
        last = ''
        while True:
            self.logger.info(f'fetching cid from: {last}')
            fetch = self.mysql.read_many(f'select cid, collection from {self.table_artist_collection} where cid > %s '
                                         f'order by cid limit 100', (last,))
            if not fetch:
                break

            for last, brief in fetch:
                yield last, json.loads(brief)['typeMarket']

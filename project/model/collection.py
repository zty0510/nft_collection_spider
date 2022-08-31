import json

from project.config import MYSQL_CONFIG
from project.utils.logger import Log
from project.utils.mysql_helper import Mysql


class Collection:
    mysql = Mysql(MYSQL_CONFIG)
    table = 'digital_collection'
    table_raw = 'digital_collection_raw'
    logger = Log(table)
    data_columns = ('name', 'platform_id', 'image', 'cover', 'author_name', 'description',
                    'issue_price', 'amount', 'contract_address', 'nft_id', 'chain_contract', 'chain_name',
                    'market_type')

    def exist(self, cid):
        return bool(self.mysql.read_one(f'select commodity_id from {self.table} where '
                                        f'commodity_id = %s', (cid,)))

    def save_parsed(self, parsed):
        cid = parsed.pop('commodity_id')
        if self.exist(cid):
            return self.mysql.write('update {} set {} where commodity_id = %s'.format(
                self.table, ','.join('{} = %s'.format(k) for k in self.data_columns)),
                [parsed[k] for k in self.data_columns] + [cid])
        self.mysql.write('insert into {} ({}) values ({})'.format(
            self.table, ','.join(self.data_columns), ','.join(['%s'] * len(self.data_columns))),
            [parsed[k] for k in self.data_columns])

    def read_one_collection_brief(self, platform, cid):
        fetch = self.mysql.read_one(f'select raw_content from {self.table_raw} where '
                                    f'commodity_id = %s and platform = %s', (cid, platform))
        brief = fetch[0] if fetch else None
        return json.loads(brief) if brief else None

    def save_raw(self, cid, item_id, platform, raw, detail, only_brief=False):
        self.logger.info(f'saving item: {item_id}')
        exist = self.mysql.read_one(f'select item_id from {self.table_raw} where commodity_id = %s and item_id = %s',
                                    (cid, item_id))
        raw = json.dumps(raw)
        detail = json.dumps(detail) if detail else ''
        if exist:
            return
            # if only_brief:
            #     self.mysql.write(f'update {self.table_raw} set raw_content = %s where '
            #                      f'commodity_id = %s and item_id = %s', (raw, cid, item_id))
            # else:
            #     self.mysql.write(f'update {self.table_raw} set raw_content = %s, raw_detail = %s where '
            #                      f'commodity_id = %s and item_id = %s', (raw, detail, cid, item_id))
        else:
            self.mysql.write(f'insert into {self.table_raw} (commodity_id, item_id, platform, raw_content, '
                             f'raw_detail) values (%s, %s, %s, %s, %s)',
                             (cid, item_id, platform, raw, detail))

    def update_detail(self, cid, item_id, platform, detail):
        # self.logger.info(f'updating cid: {cid}, item_id: {item_id}, platform: {platform}')
        self.mysql.write(f'update {self.table_raw} set raw_detail = %s where '
                         f'commodity_id = %s and item_id = %s and platform = %s',
                         (json.dumps(detail), cid, item_id, platform))

    def read_all_commodities_with_content(self, platform):
        self.logger.info('fetching all commodities with content')
        fetch = self.mysql.read_many(f'select commodity_id, raw_content from {self.table_raw} where '
                                     f'platform = %s group by commodity_id',
                                     (platform,))
        return [(c, json.loads(content)) for c, content in fetch]

    def read_all_commodities(self, platform):
        self.logger.info('fetching all commodities')
        fetch = self.mysql.read_many(f'select distinct commodity_id from {self.table_raw} where '
                                     f'platform = %s ', (platform,))
        return {c for c, in fetch}

    def read_all_items(self, platform):
        fetch = self.mysql.read_many(f'select item_id from {self.table_raw} where platform = %s', (platform,))
        return [i for i, in fetch]

    def read_detail_by_item(self, platform, cid, item_id):
        fetch = self.mysql.read_one(f'select raw_detail from {self.table_raw} where '
                                    f'platform = %s and commodity_id = %s and item_id = %s',
                                    (platform, cid, item_id))
        return json.loads(fetch[0]) if fetch else None

    def read_commodity_items_id(self, platform, cid):
        fetch = self.mysql.read_many(f'select item_id from {self.table_raw} where platform = %s and commodity_id = %s',
                                     (platform, cid))
        return [i for i, in fetch]


if __name__ == '__main__':
    print(Collection().read_one_collection_brief(1, 'f050f5a4bdcbbe2b30635665505b4d6a'))


from itertools import product, chain
from hashlib import md5

from project.model.spider.mints import MINTS
from project.model.spider.sevenjft import SevenJFT
from project.utils.logger import Log
from project.model.spider.one_art import OneArt
from project.model.spider.bmark import BMark
from project.model.spider.qin import Qin
from project.model.spider.red_cave import RedCave
from project.model.spider.shicang import ShiCang
from project.model.spider.xumi import XuMi
from project.model.spider.u_banquan import UBanQuan
from project.model.spider.hi import Hi
from project.model.spider.star import Star
from project.model.spider.xinhua import XinHua
from project.model.spider.r_space import RSpace
from project.model.spider.bilibili import BiliBili
from project.model.spider.fifth import Fifth
from project.model.spider.top_holder import TopHolder
from project.model.spider.mgtv import MgTV
from project.model.spider.jd_lingxi import JD_LingXi
from project.model.spider.lingjing import LingJing
from project.model.spider.bbyz import BBYZ

from project.model.collection import Collection
from project.model.price import Price


class Driver:
    logger = Log('collection')
    collection = Collection()

    def bbyz(self):
        api = BBYZ()
        for brief in api.get_all_collections():
            self.collection.save_raw(brief['commodity_id'], '0' * 32, api.PLATFORM_ID, brief, None, True)

    def lj(self):
        api = LingJing()
        for brief in api.fetch_all_collections():
            self.collection.save_raw(brief['id'], '0' * 32, api.PLATFORM_ID, brief, None, True)

    def jd_lx(self):
        api = JD_LingXi()
        for brief, detail in api.get_all_collections():
            cid = md5(f'{brief["goodsId"]}-jd_lx'.encode('utf8')).hexdigest()
            brief['commodity_md5'] = cid
            self.collection.save_raw(cid, '0' * 32, api.PLATFORM_ID, brief, detail)

    def mg_tv(self):
        api = MgTV()
        for brief in api.fetch_all_collections():
            self.collection.save_raw(brief['commodity_md5'], '0' * 32, api.PLATFORM_ID, brief, None, True)

    def top_holder(self):
        api = TopHolder()
        for brief, detail in api.fetch_all_collections():
            self.collection.save_raw(brief['commodity_md5'], '0' * 32, api.PLATFORM_ID, brief, detail)

    def fifth(self):
        api = Fifth()
        for brief, detail in chain(api.fetch_calendar(), api.fetch_before(), api.fetch_home_collections()):
            self.collection.save_raw(brief['commodity_md5'], '0' * 32, api.PLATFORM_ID, brief, detail)

    def bilibili(self):
        api = BiliBili()
        for brief, detail in api.fetch_all_collections():
            self.collection.save_raw(brief['commodity_id'], '0' * 32, api.PLATFORM_ID, brief, detail)

    def r_space(self):
        api = RSpace()
        for c in api.fetch_all_collections():
            self.collection.save_raw(c['commodity_id'], '0' * 32, api.PLATFORM_ID, c, None, True)

    def xinhua(self):
        api = XinHua()
        for c in api.fetch_all_collections():
            self.collection.save_raw(c['uuid'], '0' * 32, api.PLATFORM_ID, c, None, True)

    def star(self):
        api = Star()
        for collection in api.fetch_all_collections():
            cid = collection['worksNumber']
            cid_hash = md5(f'{cid}-star'.encode('utf8')).hexdigest()
            item_id = '0' * 32
            self.collection.save_raw(cid_hash, item_id, api.PLATFORM_ID, collection,
                                     api.fetch_collection_detail(cid))

    def hi(self):
        api = Hi()
        for item in api.fetch_all_collections():
            cid = item['id']
            detail = api.fetch_detail(cid)
            commodity_hash = md5(f'{cid}-hi'.encode('utf8')).hexdigest()
            item_id_hash = '0' * 32
            self.collection.save_raw(commodity_hash, item_id_hash, api.PLATFORM_ID, item, detail)

    def ubanquan(self):
        api = UBanQuan()
        for item in api.get_all_collections():
            item_id = item['auctionNo']
            detail = api.get_collection_detail(item_id)
            if not detail or not detail["nftInfoDetailVO"]:
                continue
            commodity_hash = md5(f'{detail["nftInfoDetailVO"]["contractAddress"]}-ubq'.encode('utf8')).hexdigest()
            item_id_hash = md5(f'{item_id}-ubq'.encode('utf8')).hexdigest()
            self.collection.save_raw(commodity_hash, item_id_hash, api.PLATFORM_ID, item, detail)

    def xumi(self, only_brief=False):
        api = XuMi()
        for item in api.fetch_all_items():
            item_id = item["auctionBasic"]["itemId"]
            detail = api.fetch_item_detail(item_id) if not only_brief else None
            self.collection.save_raw(item['commodity_id'], item['item_id_hash'], api.PLATFORM_ID, item, detail,
                                     only_brief)

    def shicang(self):
        api = ShiCang()
        for info in api.fetch_all_collections():
            self.collection.save_raw(info['hash_id'], info['item_id'], api.PLATFORM_ID, info, None, True)

    def red_cave(self):
        api = RedCave()
        for info in api.fetch_all_collections():
            self.collection.save_raw(info['hash_id'], info['item_id'], api.PLATFORM_ID, info, None, True)

    def bmark(self, only_brief=False):
        api = BMark()
        for brief in api.get_all_collections():
            detail = api.get_sell_detail(brief['sellId']) if not only_brief else None
            self.collection.save_raw(brief['collection_id_md5'], brief['edition_id_md5'], api.PLATFORM_ID,
                                     brief, detail, only_brief)

    def qin(self):
        api = Qin()
        price = Price()
        for brief in api.get_all_collections():
            cid = brief['cid_md5']
            self.collection.save_raw(cid, brief['gid_hash'], api.PLATFORM_ID, brief, None, True)
            price.save_prices(api.PLATFORM_ID, cid, list(api.get_collection_sale_records(brief['id'])))

    # def one_art_v2(self):
    #     api = OneArt()
    #     for category in api.get_all_categories():
    #         self.logger.info(f'fetching category: {category}')
    #
    #         for record in api.get_sale_record_list(category):
    #             pass

    def one_art(self, only_brief=False):
        api = OneArt()
        commodity_pool = set()
        item_pool = set()
        for category in api.get_all_categories(True):
            self.logger.info(f'fetching category: {category}')
            for order, desc in product((1, 2), (1, 2)):
                self.logger.info(f'order: {order}, {desc}')
                for collection in api.get_collections_by_category(category, order, desc):
                    if not collection:
                        continue
                    commodity = collection['commodity']
                    cid = commodity['id']
                    item_id = collection['id']
                    if item_id not in item_pool:
                        item_pool.add(item_id)
                        detail = None if only_brief else api.get_item_detail(item_id)
                        self.collection.save_raw(cid, item_id, api.PLATFORM_ID, collection, detail, only_brief)
                    # if cid in commodity_pool:
                    #     continue
                    # commodity_pool.add(cid)
                    # old error progress
                    # self.logger.info(f'saving: {commodity["name"]}')
                    # self.collection.save_parsed({
                    #     'commodity_id': cid,
                    #     'name': commodity['name'],
                    #     'platform_id': api.PLATFORM_ID,
                    #     'image': commodity['actualPicture'],
                    #     'cover': commodity['cover'],
                    #     'author_name': collection['author']['name'],
                    #     'description': commodity['description'],
                    #     'issue_price': commodity['price'],
                    #     'amount': commodity['amountSku'],
                    #     'contract_address': commodity['contractAddress'],
                    #     'nft_id': collection['commoditySku']['nftId'],
                    #     'chain_contract': commodity['chainContract'],
                    #     'chain_name': commodity['chainName'],
                    #     'market_type': commodity['typeMarket']
                    # })
        self.logger.info(f'total commodity: {len(commodity_pool)}')
        self.logger.info(f'total items: {len(item_pool)}')

    # def patch_one_art(self):
    #     api = OneArt()
    #     for cid in self.collection.read_all_commodities(api.PLATFORM_ID):
    #         for item_id in self.collection.read_commodity_items_id(api.PLATFORM_ID, cid):
    #             self.collection.update_detail(cid, item_id, api.PLATFORM_ID, api.get_item_detail(item_id))
    def seven_jft(self):
        api = SevenJFT()
        for data in api.search_all_work():
            self.collection.save_raw(data[0], data[1], data[2], data[3], data[4])
            # print((data[0], data[1], data[2], data[3], data[4]))
        self.logger.info(f'fetch seven_jft over')

    def mints(self):
        api = MINTS()
        for data in api.get_all_list():
            self.collection.save_raw(data['commodity_id'], data['item_id'], api.PLATFORM_ID, data['collection'], data['item_detail'])
        self.logger.info(f'fetch mints over')


if __name__ == '__main__':
    Driver().mints()

import time
import traceback

from project.model.spider.one_art import OneArt
from project.model.spider.bmark import BMark
from project.model.price import Price
from project.model.collection import Collection
from project.utils.logger import Log


class Driver:
    logger = Log('price')
    price_model = Price()

    # def sync(self, max_page=0):
    #     self.one_art(max_page)

    def _one_art_single(self, max_page=0):
        api = OneArt()
        platform = api.PLATFORM_ID
        for cid, content in Collection().read_all_commodities_with_content(platform):
            prices = []
            if content['commodity']['typeMarket'] != 2:
                continue
            self.logger.info(f'fetching for: {cid}')
            for p in api.get_collection_prices(cid, max_page):
                prices.append([p['time'] + ':00:00', p['price']])
            if not prices:
                self.logger.info('skip for empty prices')
                continue
            self.price_model.save_prices(platform, cid, prices)

    def one_art(self, max_page=10):
        while True:
            try:
                self._one_art_single(max_page)
            except Exception:
                self.logger.error(traceback.format_exc())

    # def one_art_active(self, max_page=0):
    #     api = OneArt()
    #     platform = api.PLATFORM_ID
    #     cids = self.price_model.read_all_commodity_by_platform(platform)
    #     self.logger.info(f'total active cids: {len(cids)}')
    #     for cid in cids:
    #         prices = []
    #         self.logger.info(f'fetching for: {cid}')
    #         for p in api.get_collection_prices(cid, max_page):
    #             prices.append([p['time'] + ':00:00', p['price']])
    #         self.price_model.save_prices(platform, cid, prices)

    def bmark(self):
        api = BMark()
        platform = api.PLATFORM_ID
        collection = Collection()
        for commodity in collection.read_all_commodities(platform):
            result = {}
            for item_id in collection.read_commodity_items_id(platform, commodity):
                detail = collection.read_detail_by_item(platform, commodity, item_id)
                if not detail:
                    continue
                result[item_id] = list(api.get_sale_record(detail['assetsId']))
            self.price_model.save_prices(platform, commodity, result)



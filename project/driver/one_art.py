import datetime
import json
import random
import time
import traceback

from concurrent.futures import ThreadPoolExecutor
from threading import Lock

import requests

from project.config import ENABLE_PROXY
from project.utils.logger import Log
from project.model.spider.one_art import OneArt
from project.model.the_one_artist import TheOneArtist
from project.model.theone_latest import TheOneLatestPublish


class Driver:
    logger = Log('one-art-driver')

    idx = 0
    proxy_idx = 0

    api_lock = Lock()
    proxy_lock = Lock()

    def __init__(self):
        self._proxies = None
        self.one_art = OneArt()
        self.apis = None

    def _get_api(self):
        with self.api_lock:
            if not self.apis:
                self.apis = [OneArt('', self.one_art.get_signature()) for _ in range(200)]
            self.idx += 1
            # self.logger.info(f'using api idx: {self.idx}')
            return self.apis[self.idx % len(self.apis)]

    def _get_next_proxy(self):
        with self.proxy_lock:
            if not self._proxies:
                self._proxies = self._get_available_proxies()

            self.proxy_idx += 1
            return self._proxies[self.proxy_idx % len(self._proxies)]

    def _get_available_proxies(self):
        if not ENABLE_PROXY:
            return []
        self.logger.info('fetching proxy pools')
        resp = requests.get('http://10.0.0.226:9000/api/ip').json()['data']
        return [{
            'https': p
        } for p in resp]

    def collection_by_artist(self):
        start = time.time()
        api = OneArt()
        artist_model = TheOneArtist()
        for artist in api.fetch_all_artist():
            aid = artist['uuid']
            artist_model.save_artist(aid, artist)
            for collection in api.fetch_artist_gallery(aid):
                cid = collection['id']
                artist_model.save_gallery(aid, cid, collection)
        self.logger.info(f'total spend: {time.time() - start}')

    def collection_lowest_price(self):
        artist_model = TheOneArtist()
        batch = []
        start_ts = int(time.time())
        for cid, m_type in artist_model.fetch_all_collections():
            price = self._get_api().fetch_commodity_lowest_price(cid, m_type)
            if price is not None:
                batch.append((start_ts, cid, price))
                if len(batch) >= 30:
                    artist_model.batch_save_lowest_price(batch)
                    batch = []
        if batch:
            artist_model.batch_save_lowest_price(batch)
        self.logger.info(f'collection_lowest_price total spend: {time.time() - start_ts}')

    def concurrent_lowest_price(self, pool_size=200):
        while True:
            self._proxies = None
            self.proxy_idx = 0
            self.idx = 0
            artist_model = TheOneArtist()

            start_ts = int(time.time())

            def labor(group):
                batch = []
                for cid, m_type in group:
                    try:
                        price = self._get_api().fetch_commodity_lowest_price(cid, m_type, self._get_next_proxy())
                        if price is None:
                            continue
                        batch.append((start_ts, cid, price))
                    except:
                        self.logger.error(traceback.format_exc())
                        continue
                if batch:
                    artist_model.batch_save_lowest_price(batch)

            def cut_groups():
                group = []
                for cid, m_type in artist_model.fetch_all_collections():
                    if m_type != 2:
                        continue
                    group.append((cid, m_type))
                    if len(group) >= 1:
                        yield group
                        group = []
                if group:
                    yield group

            pool = ThreadPoolExecutor(pool_size)
            for _ in pool.map(labor, cut_groups()):
                pass
            self.logger.info(f'total spend: {time.time() - start_ts}')

    # def latest_published_record(self):
    #     while True:
    #         apis = (OneArt(ONE_ART_AUTH, ONE_ART_SIG),
    #                 OneArt('eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiIxMzUyNDY2MjY5OCIsImlhdCI6MTY1ODEzMjYzNCwiZXhwIjoxNjU4NzM3NDM0fQ.xzROhIn17JIegoMLA96v2pdzTfoqRDgudTogRKyZuyexnVNIn4N7Sbt1wD3WWz9k2Oy-Kz3VmgWAq3KK2vtK8g',
    #                        'urAXnH74o6RUliX95C+NtuZ9fTlJRBXlRDDfWiReOVNnHbp6nlJCrVwPKkYsKXWstTcKYdY8iz4q9s2PdNTE6A=='),
    #                 OneArt('eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiIxNzMxNzUzMzE0NiIsImlhdCI6MTY1ODEzNjEwMCwiZXhwIjoxNjU4NzQwOTAwfQ._Y36A0-xmtGt4Y2Um_AZ31vur9fUmOpNaB_YL5XLPGvO6lBaLxS0hThKkUAcI9-FMgH2bhcxykcCWtBr3jBJ3A',
    #                        'OasvnXKthNqJdSvHX+NZh87HMZ9Jk384d2dTdY0SAc7JcqTYRGzgF06448gkPO/Y+AFbO+GEm3mTzb9NjG+k8A=='),
    #                 OneArt('', 'P7Sqf4as/P5DIz2WSoOe4fauGcxh/42gMD8WkVLgOyO1O/+0v40qBNnzCGZJriH+snfo2Ty0BVdSnYXI9NNYTw=='),
    #                 OneArt('', '27Yo7tbbEttOMbl0/jGxwOaLLHE7MrrJHUi0uwAWJ2nYIcFq2Ly2ujpEYVWP92+bvoLgm4tpZ0LR81OAOU6qSw=='))
    #         api = random.choice(apis)
    #         saver = TheOneLatestPublish()
    #         start = time.time()
    #         record = datetime.datetime.now()
    #         order = 1
    #         desc = 2
    #         self.logger.info(f'order: {order}, {desc}')
    #         batch = []
    #         for category in api.get_all_categories():
    #             self.logger.info(f'fetching category: {category}')
    #             for collection in api.get_collections_by_category(category, order, desc, 30):
    #                 if not collection:
    #                     continue
    #                 cid = collection['commodity']['id']
    #                 item_id = collection['id']
    #                 batch.append((record, cid, item_id, collection['price']))
    #                 if len(batch) >= 100:
    #                     saver.save_batch(batch)
    #                     batch = []
    #         if batch:
    #             saver.save_batch(batch)
    #         self.logger.info(f'time spend: {time.time() - start}')
    #         time.sleep(120)

    def concurrent_latest_publish(self):
        while True:
            record = datetime.datetime.now()
            pool = ThreadPoolExecutor(3)

            def category_labor(category):
                api = self._get_api()
                self.logger.info(f'fetching category: {category}')
                saver = TheOneLatestPublish()
                batch = []
                for collection in api.get_collections_by_category(category, 1, 2, 30):
                    if not collection:
                        continue
                    cid = collection['commodity']['id']
                    item_id = collection['id']
                    batch.append((record, cid, item_id, collection['price']))
                    if len(batch) >= 50:
                        saver.save_batch(batch)
                        batch = []
                if batch:
                    saver.save_batch(batch)

            start = time.time()
            for _ in pool.map(category_labor, self._get_api().get_all_categories()):
                pass
            self.logger.info(f'time spent: {time.time() - start}')


# if __name__ == '__main__':
#     Driver().concurrent_latest_publish()

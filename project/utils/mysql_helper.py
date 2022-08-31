import time
import traceback
from hashlib import md5
from contextlib import closing, contextmanager
from threading import Lock

import pymysql

from project.utils.logger import Log

_MANAGER_LOCKS = Lock()


class Mysql(object):
    INSTANCE = {}
    logger = Log('mysql')

    def __new__(cls, config, using_dict=False):
        s = ''.join(map(lambda i: f'{i[0]}{i[1]}', sorted(config.items()))) + str(using_dict)
        config_hash = md5(s.encode('utf8')).hexdigest()
        if config_hash in cls.INSTANCE:
            return cls.INSTANCE[config_hash]

        with _MANAGER_LOCKS:
            if config_hash not in cls.INSTANCE:
                instance = object.__new__(cls)
                instance.config = {**config, 'charset': 'utf8'}
                if using_dict:
                    from pymysql.cursors import DictCursor
                    instance.config['cursorclass'] = DictCursor
                cls.INSTANCE[config_hash] = instance
        return cls.INSTANCE[config_hash]

    @contextmanager
    def context(self, commit=False):
        with closing(pymysql.connect(**self.config)) as con:
            yield con.cursor()
            if commit:
                con.commit()

    def read_many(self, sql, args=None, _retry=0):
        if _retry > 3:
            raise Exception('mysql max read many retry exceeded')
        try:
            with self.context() as cursor:
                cursor.execute(sql, args)
                return cursor.fetchall()
        except:
            self.logger.error(traceback.format_exc())
            time.sleep(2)
            return self.read_many(sql, args, _retry + 1)

    def read_one(self, sql, args=None, _retry=0):
        if _retry > 3:
            raise Exception('mysql max read one retry exceeded')
        try:
            with self.context() as cursor:
                cursor.execute(sql, args)
                ret = cursor.fetchone()
                return ret if ret else None
        except:
            self.logger.error(traceback.format_exc())
            time.sleep(2)
            return self.read_one(sql, args, _retry + 1)

    def write(self, sql, args=None, _retry=0):
        if _retry > 3:
            raise Exception('mysql max read retry exceeded')
        try:
            with self.context(True) as cursor:
                return cursor.execute(sql, args)
        except:
            self.logger.error(traceback.format_exc())
            time.sleep(2)
            return self.write(sql, args, _retry + 1)




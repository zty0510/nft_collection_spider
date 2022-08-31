import json
import logging

from time import strftime

from project.version import __VERSION__


class Log(object):
    INSTANCE = {}
    LOGGERS = {}

    def __new__(cls, name='default'):
        if name in cls.INSTANCE:
            return cls.INSTANCE[name]

        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        channel = logging.StreamHandler()
        channel.setFormatter(logging.Formatter('%(message)s'))
        logger.addHandler(channel)
        cls.LOGGERS[name] = logger
        cls.INSTANCE[name] = object.__new__(cls)
        return cls.INSTANCE[name]

    def __init__(self, name='default'):
        self._logger = self.LOGGERS[name]
        self._label_name = name

    def format(self, level, msg):
        return json.dumps({
            'label': self._label_name,
            'level': level,
            'msg': msg,
            't': strftime('%Y-%m-%d %H:%M:%S'),
            'v': __VERSION__
        }, ensure_ascii=False, default=str)

    def info(self, msg):
        return self._logger.info(self.format('INFO', msg))

    def error(self, msg):
        return self._logger.error(self.format('ERROR', msg))

    def critical(self, msg):
        return self._logger.critical(self.format('CRITICAL', msg))


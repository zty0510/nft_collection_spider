
import os
import time
import traceback
from fnmatch import fnmatch
from importlib import import_module
from concurrent.futures import ThreadPoolExecutor

from project.utils.reporter import ding_report


def entry():
    modules = []

    for _, _, targets in os.walk(os.path.join(os.path.dirname(__file__), './driver')):
        for t in filter(lambda i: fnmatch(i, '*.py') and i != '__init__.py', sorted(targets)):
            modules.append(getattr(import_module(f'project.driver.{t[:-3]}'), 'Driver'))
    print(modules)

    methods = []

    # pool = ThreadPoolExecutor()
    for mod in modules:
        instance = mod()
        for k, v in mod.__dict__.items():
            if callable(v) and not k.startswith('_') and not k.startswith('concurrent'):
                methods.append(getattr(instance, k))
    print(methods)

    def labor(m):
        while True:
            try:
                m()
            except KeyboardInterrupt:
                pass
            except:
                ding_report(traceback.format_exc())
            print("sleep 1h for next round")
            time.sleep(3600)

    pool = ThreadPoolExecutor(len(methods))
    for _ in pool.map(labor, methods):
        pass


if __name__ == '__main__':
    entry()

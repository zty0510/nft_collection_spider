
import os
from fnmatch import fnmatch
from importlib import import_module
from argparse import ArgumentParser


def entry():
    parse = ArgumentParser()
    parse.add_argument('module', nargs='?', help='module name')
    parse.add_argument('method', nargs='?', help='method name')
    parse.add_argument('extra', nargs='*', help='extra args')
    args = parse.parse_args()

    module = args.module
    method = args.method
    extra = [eval(v) for v in args.extra]

    if not module:
        print('available modules are:\n')
        for _, _, targets in os.walk(os.path.join(os.path.dirname(__file__), './driver')):
            for t in filter(lambda i: fnmatch(i, '*.py') and i != '__init__.py',
                            sorted(targets)):
                print(t[:-3])
        return

    try:
        mod = getattr(import_module(f'project.driver.{module}'), 'Driver')
    except ImportError:
        print(f'no such driver as: {module}')
        return

    if not method:
        if mod.__doc__:
            print(mod.__doc__)
        print('available methods are:\n')
        for k, v in mod.__dict__.items():
            if callable(v) and not k.startswith('_'):
                print(k)
        return

    getattr(mod(), method)(*extra)
    # try:
    #
    # except:
    #     traceback.print_exc()

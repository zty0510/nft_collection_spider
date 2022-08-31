
from datetime import datetime


def date_int_2_date_str(date, fmt='%Y-%m-%d'):
    return datetime.strptime(str(date), '%Y%m%d').strftime(fmt)


def timestamp_2_date_int(ts):
    return int(datetime.fromtimestamp(ts).strftime('%Y%m%d'))


def date_str_2_date_int(date):
    return int(datetime.strptime(date, '%Y-%m-%d').strftime('%Y%m%d'))


import base as c
from pandas import DataFrame as d
d.to_sql

class Stock(object):

    def get_codes(self):
        all_data = c.ts.get_today_all()
        subset = all_data[['code', 'name', 'nmc']]
        stocks = [tuple(x) for x in subset.values]
        return stocks
    
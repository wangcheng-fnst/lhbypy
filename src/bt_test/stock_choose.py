import data
import pandas as pd
import talib as ta
import strategys
import stock_pool as sp
from src.bt_test import dto
import run_strategy as rs

# 使用最近一年的数据来筛选
def choose_stock(strategy,p):
    # all code
    stock_datas = sp.get_all('2021-01-01', '2022-01-01')
    hit_codes = []
    for code in stock_datas.keys():
        stock_data = stock_datas.get(code)
        if stock_data.index.size > 180:
            if strategy.judge_stock(stock_data, p):
                hit_codes.append(code)
    hit_stock_datas = [{c: stock_data.get(c)} for c in hit_codes]
    if strategy is strategys.JXDTStrategy:
        result = rs.test_jx(hit_stock_datas, model='choose')



choose_stock(strategys.JXDTStrategy,dto.JXDto('', 5, 10, 20, 180, '均线-1', 100000))
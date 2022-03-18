import data
import pandas as pd
import talib as ta
import strategys
import stock_pool as sp
from src.bt_test import dto
import run_strategy as rs
import strategy_result_analysis as sra
import src.common.constants as constants

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
    hit_stock_datas = {}
    for c in hit_codes[100:100]:
        hit_stock_datas.update({c: stock_datas.get(c)})
    if strategy is strategys.JXDTStrategy:
        print('choose jx, data count : %i' % (len(hit_stock_datas.keys())))
        if len(hit_stock_datas.keys()) < 1:
            return
        result = rs.test_jx(hit_stock_datas, model='choose')
        sra.handle_strategy_result(result, constants.get_result_path('choose/jx/'))



choose_stock(strategys.JXDTStrategy,dto.JXDto('', 5, 10, 20, 180, '均线-1', 100000))
import data
import pandas as pd
import talib as ta
import strategys

def choose_stock(strategy,p):
    # all code
    codes = data.read_stock_code()
    codes = codes.loc[1000:1020]
    hit_codes=[]
    for code in codes['code']:
        # 多线程
        stock_data = data.get_online_data(str(code))
        if stock_data is not None:
            if strategy.judge_stock(stock_data,p):
                hit_codes.append(code)
    print(hit_codes)

choose_stock(strategys.JXDTStrategy)
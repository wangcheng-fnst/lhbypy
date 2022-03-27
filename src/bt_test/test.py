from concurrent.futures import ThreadPoolExecutor,wait,ALL_COMPLETED
import tushare as tu
import pandas as pd
import datetime
import bao_stock

executor = ThreadPoolExecutor(max_workers=1)

def task(code, stock_data):
    df = bao_stock.get_k_bao_online(code)
    stock_data.update({code: df})

stock_codes = pd.read_csv('stock.csv')
stock_codes = stock_codes['code'].iloc[2000:2100]
stock_data ={}



begin = datetime.datetime.now()
all_task = [executor.submit(task, str(code), stock_data) for code in stock_codes]
wait(all_task, return_when=ALL_COMPLETED)
end = datetime.datetime.now()
cost = (end -begin).seconds
print('cost %i' % (cost))
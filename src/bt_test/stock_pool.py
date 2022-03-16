import baostock as bs
import akshare as ak
from concurrent.futures import ThreadPoolExecutor,wait,ALL_COMPLETED, as_completed
import pandas as pd
import bao_stock
import datetime
import talib as ta
import time
from sqlalchemy import create_engine

engine = create_engine('mysql+pymysql://stock_db:P4WSfPDzKL3ykbCz@42.192.15.190:3306/stock_db')

executor = ThreadPoolExecutor(max_workers=10)
# 中证50
def get_zz50():

    pass

# 中证500
def get_zz500():
    begin = datetime.datetime.now()
    # 登陆系统
    lg = bs.login()
    rs = bs.query_zz500_stocks()
    # lg = bs.logout()
    # 打印结果集
    stocks = []
    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        stocks.append(rs.get_row_data())
    result = pd.DataFrame(stocks, columns=rs.fields)
    stock_datas = {}
    # bs.login()
    all_tasks = [executor.submit(get_stock_data, code, stock_datas) for code in result['code']]
    wait(all_tasks, return_when=ALL_COMPLETED)
    bs.logout()
    end = datetime.datetime.now()
    cost = (end - begin).seconds
    print('cost %i' % cost)
    return stock_datas

# 根据市值取股池，单位亿
def get_value(min= 100, max= 2000):
    pass

# 次新股池


def get_stock_data(code, start_date, end_date):
    start = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    stock_df = ak.stock_zh_a_hist(symbol=code, adjust='hfq', start_date=start_date, end_date=end_date)
    if stock_df.empty:
        print('+++++++code=%s is none+++++++' % code)
        return code, None
    stock_df = stock_df.rename({'开盘': 'open',
                                '收盘': 'close',
                                '最高': 'high',
                                '最低': 'low',
                                '成交量': 'volume',
                                '成交额': 'amount',
                                '换手率': 'turn',
                                '日期': 'date'},
                               axis='columns')
    stock_df.index = pd.to_datetime(stock_df['date'])
    stock_df.index.name = 'date'
    stock_df['code'] = code
    try:
        base_df = ak.stock_a_lg_indicator(code)
        base_df.index = pd.to_datetime(base_df['trade_date'])
        t = base_df.loc[end:start].sort_index()
        t.index.name = 'date'
        stock_df[['pe', 'pb', 'total_mv']] = t[['pe', 'pb', 'total_mv']]
    except Exception as e:
        print('=============code= %s,e=%s' % (code, e))
        stock_df[['pe', 'pb', 'total_mv']] = 0
        # 计算每日量比
    stock_df['lb'] = stock_df['volume'] / ta.SMA(stock_df['volume'], timeperiod=5)
    # print(code)
    try:
        stock_df.to_sql('stock_data', engine, index=False, if_exists='append')
        time.sleep(0.1)
    except Exception as e:
        print('=============insert error= %s,e=%s'% (code, e))
    return code, stock_df



def get_all_stock_pool(start_date, end_date):
    begin = datetime.datetime.now()
    stock_datas = {}
    all_stock_df = ak.stock_zh_a_spot_em()
    i = 0

    for code in all_stock_df['代码']:
        all_tasks = []
        all_tasks.append(executor.submit(get_stock_data, code, start_date, end_date))
        i += 1
        if i >= 200:
            c_b = datetime.datetime.now()
            for task in as_completed(all_tasks):
                try:
                    r_code, data = task.result()
                    if data is None:
                        continue
                    # print('code=%s finished' % r_code)
                    stock_datas.update({r_code: data})
                except Exception as e:
                    print(e)

            c_e = datetime.datetime.now()
            c_cost = (c_e - c_b).seconds
            print('c_cost:%i' % c_cost)
            i = 0
        all_tasks.clear()
        # time.sleep(10)


    # all_tasks = [executor.submit(get_stock_data, code, start_date, end_date) for code in all_stock_df['代码']]

    end = datetime.datetime.now()
    cost = (end - begin).seconds
    print('cost %i' % cost)
    print(len(all_tasks))
    print(len(stock_datas.keys()))
    pass

# get_all_stock_pool('2018-01-01', '2022-03-15')

def get_stock_basic(code, start_date, end_date):
    try:
        start = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.datetime.strptime(end_date, '%Y-%m-%d')
        base_df = ak.stock_a_lg_indicator(code)
        base_df = base_df.rename({'trade_date':'date'}, axis='columns')
        base_df.index = pd.to_datetime(base_df['date'])
        t = base_df.loc[end:start].sort_index()
        t['code'] = code
        t.to_sql('stock_basic_data', engine, index=False, if_exists='append')

    except Exception as e:
        print('get_stock_basic error: %s, error:%s' % (code, e))
    return code


def get_writed_codes():
    writed_codes = pd.read_sql('select distinct code from stock_basic_data', engine)


def write_stock_basic(start_date, end_date):
    all_stock_df = ak.stock_zh_a_spot_em()
    i = 0
    for code in all_stock_df['代码']:
        all_tasks = []
        all_tasks.append(executor.submit(get_stock_basic, code, start_date, end_date))
        i +=1
        if i >= 100:
            for task in as_completed(all_tasks):
                b_code = task.result()
        i = 0
        all_tasks.clear()

write_stock_basic('2018-01-01','2022-03-15')

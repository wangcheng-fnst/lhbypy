import pandas as pd
import tushare as tu
import baostock as bs
import datetime


def write_data(code, start=None, end=None):
    df = tu.get_k_data(code=code)
    filename = code + '.csv'
    df.to_csv(filename)
    return df


def read_data(code, start='2000-01-01', end='2200-01-01'):
    filename = code + '.csv'

    df = pd.read_csv(filename, index_col='date', parse_dates=['date'])
    df['OpenInterest'] = 0
    df = df[['open', 'close', 'high', 'low', 'volume', 'OpenInterest']]
    df.loc[start:end]
    return df


def write_stock_code():
    codes = tu.get_today_all()
    file = "stock.csv"
    codes.to_csv(file)
    return codes


def read_stock_code():
    file = "stock.csv"
    return pd.read_csv(file)[['code']]


def get_online_data(code):
    df = tu.get_k_data(code=code)
    if not df.empty:
        df.index = pd.to_datetime(df['date'])
        return df[['open', 'close', 'high', 'low', 'volume', 'code']]
    return None


def read_hs_300_code():
    return pd.read_csv('hs300.scv')['code']


def write_hs_300_code():
    # 登陆系统
    lg = bs.login()
    # 获取沪深300成分股
    rs = bs.query_hs300_stocks()
    lg = bs.logout()
    # 打印结果集
    hs300_stocks = []
    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        hs300_stocks.append(rs.get_row_data())
    result = pd.DataFrame(hs300_stocks, columns=rs.fields)
    result.to_csv('hs300.scv')

write_hs_300_code()

# write_stock_code()
#
# print(read_stock_code())

# df = write_data('600600')
# print(df)
# df = read_data('600600')
# print(df)

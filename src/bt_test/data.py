import pandas as pd
import tushare as tu
import datetime


def write_data(code, start=None, end=None):
    df = tu.get_k_data(code=code)
    filename = code+'.csv'
    df.to_csv(filename)
    return  df


def read_data(code, start = '2000-01-01', end='2200-01-01'):
    filename = code+'.csv'

    df = pd.read_csv(filename, index_col='date', parse_dates=['date'])
    df['OpenInterest'] = 0
    df = df[['open','close','high','low','volume','OpenInterest']]
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
        return df[['open', 'close', 'high', 'low', 'volume','code']]
    return None

# write_stock_code()
#
# print(read_stock_code())

# df = write_data('600600')
# print(df)
# df = read_data('600600')
# print(df)

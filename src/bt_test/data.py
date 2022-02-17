import pandas as pd
import tushare as tu


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


# df = write_data('600600')
# print(df)
# df = read_data('600600')
# print(df)

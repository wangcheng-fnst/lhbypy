from matplotlib.pyplot import get
import pandas as pd
import akshare as ak
from akshare.stock_feature.stock_em_hist import *

df = pd.DataFrame([[1, 2], [4, 5], [7, 8]],
     index=['cobra', 'viper', 'sidewinder'],
     columns=['max_speed', 'shield'])

print(df)
df.rename(columns={'max_speed':'x1'}, inplace=True)
print(df)
df.columns = ['x2','x3']

print(df)
print(df.loc[[True,True,False]])

df['x'] = False
df.loc[df.x,'xx'] = True
print(df)


def get_lhb():
    print(ak.stock_sina_lhb_ggtj(recent_day=5))
    print(ak.stock_sina_lhb_detail_daily(trade_date='20220114'))

def get_code():
    df = ak.stock_zh_a_spot_em()
    name_dict={'代码':'code','名称':'name'}

    df.rename(columns=name_dict, inplace=True)
    subset = df[['code', 'name']]
    print(subset)

def get_ashare_data(code, start, end):
    start=''.join(start.split('-'))
    end=''.join(end.split('-'))
    df = ak.stock_zh_a_hist(symbol=code, start_date=start, end_date=end, adjust='hfq')
    # 日期    开盘    收盘    最高    最低      成交量     成交额    振幅  涨跌幅  涨跌额 换手率
    name_dist = {'日期':'date','开盘':'open','收盘':'close',
                '最高':'high','最低':'low',
                '成交量':'charge','成交额':'amount','振幅':'amplitude',
                '涨跌幅':'quote_change','涨跌额':'up_down','换手率':'change_rate'}
    df.rename(columns=name_dist, inplace=True)
    return df

# get_lhb()
# get_code()

def del_error():
    for i in [10,2,0,0,3,4,0,5]:
        try:
            10/i
            print(i)
        except Exception as e:
            print('error : '+str(i))
            pass
del_error()
# print(get_ashare_data('000001','2011-01-01','2022-05-14'))
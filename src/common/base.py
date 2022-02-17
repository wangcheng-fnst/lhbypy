# 先引入后面分析、可视化等可能用到的库
import tushare as ts
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
from pyecharts.charts import Bar
import pymysql
import pyfolio as pf

# 正常显示画图时出现的中文和负号
from pylab import mpl

mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False
# 设置token
# token = '5c504ff69b5898f3db86ce4830f030c4801d15dd77fb0a213ad349b6'
# ts.set_token(token)
# pro = ts.pro_api()
engine = create_engine('mysql+pymysql://root:Root@123456@42.192.15.190:3306/db')



def get_his_data():
    pass
#   ts.get_hist_data(start='2022-01-05', end='2022-01-06')
#   ts.get_hists(start='2022-01-05', end='2022-01-06')
    # df = ts.get_sme_classified()
    # df = ts.get_concepts()
    # df = ts.top_list()
    # df = ts.moneyflow_hsgt()
    # df = ts.bar(code='600848',start_date='2022-01-05', end_date='2022-01-06')
    # df = ts.get_today_ticks(code='600848')
    # ts.get_today_all()
    # ts.get_k_data(code='600848',start='2022-01-05', end='2022-01-06')

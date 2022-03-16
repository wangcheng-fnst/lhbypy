import pandas as pd
import akshare as ak
import constants


def all_to_csv():
    all_stock_df = ak.stock_zh_a_spot_em()
    path = constants.get_result_path('stock_data')
    file = path + '/daily.csv'
    all_stock_df.to_csv(file, mode='a', header=False)

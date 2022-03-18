import akshare as ak
import src.common.constants as constants
import datetime

# 每天数据进csv
def all_to_csv():
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    all_stock_df = ak.stock_zh_a_spot_em()
    all_stock_df['date'] = today
    path = constants.get_result_path('stock_data')
    file = path + '/daily.csv'
    print(file)
    all_stock_df.to_csv(file, mode='a', header=False)



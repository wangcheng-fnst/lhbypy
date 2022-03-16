import akshare as ak
import src.common.constants as constants

def all_to_csv():

    all_stock_df = ak.stock_zh_a_spot_em()
    path = constants.get_result_path('stock_data')
    file = path + '/daily.csv'
    print(file)
    all_stock_df.to_csv(file, mode='a', header=False)



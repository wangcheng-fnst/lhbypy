from common.code import Stock
import common.base as b

df = b.get_his_data()

stocks = Stock()
codes = stocks.get_codes();
print(codes) 
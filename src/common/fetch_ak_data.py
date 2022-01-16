import base as b
import akshare as ak

start = '2001-01-01'
end = '2022-02-14'
add_sql = 'select c.* from stock_code c left join stock_k_data skd on c.code = skd.code \
         where skd.code is null'

def get_data(code, start, end):
    data = b.ts.get_k_data(code=code, autype='qfq', start=start, end=end)
    return data

def get_akshare_data(code, start, end):
    start=''.join(start.split('-'))
    end=''.join(end.split('-'))
    df = ak.stock_zh_a_hist(symbol=code, start_date=start, end_date=end, adjust='hfq')
    # 日期    开盘    收盘    最高    最低      成交量     成交额    振幅  涨跌幅  涨跌额 换手率
    name_dist = {'日期':'date','开盘':'open','收盘':'close',
                '最高':'high','最低':'low',
                '成交量':'charge','成交额':'amount','振幅':'amplitude',
                '涨跌幅':'quote_change','涨跌额':'up_down','换手率':'change_rate'}
    df.rename(columns=name_dist, inplace=True)
    df['code'] = code
    return df

def get_codes():

    subset = b.pd.read_sql("select * from stock_code", b.engine)
    if subset is None :
        all_data = b.ts.get_today_all()
        subset = all_data[['code', 'name', 'nmc']]
        stocks = [tuple(x) for x in subset.values]
        insert_sql(data=stocks,db_name='stock_code')
    else :
        stocks = [tuple(x) for x in subset.values]
    
    return stocks
        


def insert_sql(code,data, db_name, if_exists='append'):
    # 使用try...except..continue避免出现错误，运行崩溃
    try:
        if not data.empty:
            data.to_sql(db_name, b.engine, index=False, if_exists=if_exists)
            print('写入数据库成功')
        else:
            print(code+'is null')
    except BaseException as error:
        print(code +'写入数据库失败')


def process():
    stocks = get_codes()
    for stock in stocks:
        # data = get_data(code=stock[0],start=start,end=end)
        data = get_akshare_data(code=stock[0],start=start,end=end)
        insert_sql(code=stock[0],data=data, db_name='stock_ak_data')
    pass

def add():
    subset = b.pd.read_sql(add_sql, b.engine)
    stocks = [tuple(x) for x in subset.values]
    for stock in stocks:
        data = get_data(code=stock[0],start=start,end=end)
        insert_sql(code=stock[0],data=data, db_name='stock_ak_data')
    pass


if __name__ == '__main__':
    process()
    # add()
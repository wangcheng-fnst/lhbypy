from this import d
import base as b
import akshare as ak

start = '2022-01-01'
end = '2022-01-14'
add_sql = 'select c.* from stock_code c left join stock_k_data skd on c.code = skd.code \
         where skd.code is null'

def get_data(code, start, end):
    data = b.ts.get_k_data(code=code, autype='qfq', start=start, end=end)
    return data

def get_ashare_data(code, start, end):
    if code.startswith('6'):
        code='sh'+code
    else:
        code='sz'+code
    start=''.join(start.split('-'))
    end=''.join(end.split('-'))
    df = ak.stock_zh_a_daily(symbol='sh000001', start_date=start, end_date=end, adjust='hfq')
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
        


def insert_sql(data, db_name, if_exists='append'):
    # 使用try...except..continue避免出现错误，运行崩溃
    try:
        if not data.empty:
            data.to_sql(db_name, b.engine, index=False, if_exists=if_exists)
            print('写入数据库成功')
        else:
            print('is null')
    except Exception as error:
        print(data['code'][0]+'写入数据库失败'+ error)
        pass


def process():
    stocks = get_codes()
    for stock in stocks:
        # data = get_data(code=stock[0],start=start,end=end)
        data = get_ashare_data(code=stock[0],start=start,end=end)
        insert_sql(data=data, db_name='stock_k_data')
    pass

def add():
    subset = b.pd.read_sql(add_sql, b.engine)
    stocks = [tuple(x) for x in subset.values]
    for stock in stocks:
        data = get_data(code=stock[0],start=start,end=end)
        insert_sql(data=data, db_name='stock_k_data')
    pass


if __name__ == '__main__':
    process()
    # add()
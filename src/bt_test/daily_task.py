import akshare as ak
import src.common.constants as constants
import datetime
import pandas as pd
from sqlalchemy import create_engine
from concurrent.futures import ThreadPoolExecutor,wait,ALL_COMPLETED, as_completed


engine = create_engine('mysql+pymysql://stock_db:P4WSfPDzKL3ykbCz@42.192.15.190:3306/stock_db')
executor = ThreadPoolExecutor(max_workers=10)


# 每天数据进csv
def all_to_csv():
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    all_stock_df = ak.stock_zh_a_spot_em()
    all_stock_df['date'] = today
    path = constants.get_result_path('stock_data')
    file = path + '/daily.csv'
    print(file)
    all_stock_df.to_csv(file, mode='a', header=False)


def daily_to_db(today):
    # 序号	代码	名称	最新价	涨跌幅	涨跌额	成交量	成交额	振幅	最高	最低	今开	昨收	量比	换手率	市盈率-动态	市净率
    # today = datetime.datetime.now().strftime('%Y-%m-%d')
    all_stock_df = ak.stock_zh_a_spot_em()

    stock_data_df = all_stock_df[['代码', '今开', '最低', '最高', '最新价', '成交量',
                                  '换手率', '量比', '成交额','振幅', '涨跌幅', '涨跌额']]
    stock_data_df = stock_data_df.rename({'今开': 'open',
                         '最新价': 'close',
                         '最高': 'high',
                         '最低': 'low',
                         '成交量': 'volume',
                         '成交额': 'amount',
                         '换手率': 'turn',
                         '量比': 'lb',
                         '市盈率-动态': 'pe_M',
                         '市净率': 'pb'
                         },
                        axis='columns')

    all_stock_df['date'] = today


def get_stock_basic(code, start_date, success_codes, error_codes):
    try:
        # start = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        base_df = ak.stock_a_lg_indicator(code)
        base_df = base_df.rename({'trade_date':'date'}, axis='columns')
        base_df.index = pd.to_datetime(base_df['date'])
        t = base_df.loc[start_date]
        t['code'] = code
        success_codes.add(code)
        # print('success_codes add %s'%code)
        t.to_sql('stock_basic_data', engine, index=False, if_exists='append')
    except Exception as e:
        print('get_stock_basic error: %s, error:%s' % (code, e))
        error_codes.add(code)
    return code

def daily_basic_tod_db(today):
    all_stock_df = ak.stock_zh_a_spot_em()
    sql = '''select distinct code from stock_basic_data 
                    where date =''' + '\'' + today + '\''
    db_codes = pd.read_sql(sql, engine)
    flag = all_stock_df['代码'].isin(db_codes['code'])
    diff = all_stock_df[[not f for f in flag]]
    all_size = diff.index.size

    success_codes = set()
    error_codes = set()
    max_try_count = 3
    try_count = 0
    all_begin = datetime.datetime.now()
    while try_count < max_try_count:
        i = 0
        num = 0
        all_tasks = []
        for code in diff['代码']:
            if str(code).startswith('4') or str(code).startswith('8'):
                continue
            if success_codes.__contains__(code):
                continue
            all_tasks.append(executor.submit(get_stock_basic, code, today, success_codes, error_codes))
            i += 1
            num += 1
            if i >= 100:
                begin = datetime.datetime.now()
                for task in as_completed(all_tasks):
                    b_code = task.result()
                i = 0
                end = datetime.datetime.now()
                print('num =%i, cost %i' % (num, (end - begin).seconds))
                all_tasks.clear()

        print('success_size=%i, error_size=%i ' % (len(success_codes), len(error_codes)))
        try_count += 1
        if (len(error_codes)) < 300:
            break

    all_end = datetime.datetime.now()
    print('===================')
    print('success_size=%i, error_size=%i  cost=%i' % (len(success_codes), len(error_codes),
                                                       (all_end - all_begin).seconds))


# daily_basic_tod_db('2022-03-18')


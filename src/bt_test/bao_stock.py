import baostock as bs
import pandas as pd
import talib as ta
# http://baostock.com/baostock/index.php/A%E8%82%A1K%E7%BA%BF%E6%95%B0%E6%8D%AE
'''

参数名称	          参数描述	      说明
date	          交易所行情日期	  格式：YYYY-MM-DD
code	          证券代码	      格式：sh.600000。sh：上海，sz：深圳
open	          今开盘价格	  精度：小数点后4位；单位：人民币元
high	          最高价	      精度：小数点后4位；单位：人民币元
low	              最低价	精度：小数点后4位；单位：人民币元
close	          今收盘价	精度：小数点后4位；单位：人民币元
preclose	      昨日收盘价	精度：小数点后4位；单位：人民币元
volume	          成交数量	单位：股
amount	          成交金额	   精度：小数点后4位；单位：人民币元
adjustflag	      复权状态	     不复权、前复权、后复权
turn	          换手率	精度：小数点后6位；单位：%
tradestatus	      交易状态	1：正常交易 0：停牌
pctChg	          涨跌幅（百分比）	精度：小数点后6位
peTTM	          滚动市盈率	精度：小数点后6位
psTTM	          滚动市销率	精度：小数点后6位
pcfNcfTTM	      滚动市现率	精度：小数点后6位
pbMRQ	          市净率	精度：小数点后6位
isST	          是否ST	1是，0否
'''


def get_k_bao_online(code):
    if code.startswith('0') or code.startswith('3'):
        code += '.sz'
    elif code.startswith('6'):
        code += '.sh'

    lg = bs.login()
    rs = bs.query_history_k_data_plus(code,
                                      "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,isST,peTTM,pbMRQ,pcfNcfTTM",
                                      start_date='2017-07-01', end_date='2050-12-31',
                                      frequency="d", adjustflag="3")
    bs.logout()
    data_list = []
    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        data_list.append(rs.get_row_data())

    if len(data_list) > 0:
        result = pd.DataFrame(data_list, columns=rs.fields)
        result.index = pd.to_datetime(result['date'])
        rs.fields.remove('date')
        rs.fields.remove('code')
        for f in rs.fields:
            result[f] = pd.to_numeric(result[f])
        # 计算每日量比
        result['lb'] = result['volume'] / ta.SMA(result['volume'], timeperiod=5)
        return result
    return None

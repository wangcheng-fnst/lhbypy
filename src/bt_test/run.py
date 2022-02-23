import random

import backtrader as bt
import pandas as pd

import data as data
import strategys as st
import dto
from backtrader_plotting import Bokeh
from bokeh.plotting import output_file



# 对指定股票进行指定的策略回测
def run_back_test(code, strategy, strategy_dtos,res):
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    # strategy = st.JXDTStrategy
    stock_df = data.get_online_data(code)
    if stock_df is None:
        return
    stock_df['zt'] = (stock_df['close'] - stock_df.shift(1)['close']) / stock_df.shift(1)['close'] > 0.0099
    bt_data = bt.feeds.PandasData(dataname=stock_df)

    # jxP = [dto.JXDto(code,5,10,30,90,'jx_1'),dto.JXDto(code,5,20,40,180,'jx_2')]
    # cerebro.optstrategy(strategy, p=strategy_dtos)
    # cerebro.addstrategy(strategy, period=(5,20,40,90,'jx-2'))
    cerebro.addstrategy(strategy)
    # Add the Data Feed to Cerebro
    cerebro.adddata(bt_data, name=code)

    # cerebro.addobserver(bt.observers.Broker)
    # cerebro.addobserver(bt.observers.Trades)
    # cerebro.addobserver(bt.observers.BuySell)
    # cerebro.addobserver(bt.observers.DrawDown)
    # cerebro.addanalyzer(bt.analyzers.Returns, _name='_Returns', tann=252)

    # 设置投资金额1000.0
    cerebro.broker.setcash(10000.0)
    # 每笔交易使用固定交易量
    # cerebro.addsizer(bt.sizers.FixedSize, stake=100)
    # 设置佣金为0.0
    cerebro.broker.setcommission(commission=0.0005)

    back = cerebro.run(maxcpus=1)
    res_to_file(cerebro, code)
    # for p in strategy_dtos:
    #     re = back[0][0].p.item.pop(p.get_key())
    #     if re.trade_count > 0:
    #         res.append(re)


def res_to_file(cerebro, file_name):

    plotconfig = {
        'r:^Broker.*': dict(
            plotlinelabels=True,
        ),
        'r:^Trades.*': dict(
            plotlinelabels=True,
        ),

    }
    # cerebro.plot(iplot=True)
    b = Bokeh(style='bar',plotconfig=plotconfig, filename='te_res.html', output_mode='save')
    cerebro.plot(b)

# 测试均线
# for code in ['600600','600100','688303']:
#     strategy = st.JXDTStrategy
#     run_back_test(code,strategy)

# codes = data.read_stock_code().loc[1000:1100]


# 测试涨停板
def test_zt():
    res =[]
    for code in data.read_stock_code().loc[1000:1050]['code']:
        code = str(code)
        strategy = st.ZTBStrategy
        dtos = [dto.BaseStrategyDto(code, str(random.random()))]
        run_back_test(code,strategy,dtos,res)


    codes = [r.code for r in res]
    summaries = [r.summary for r in res]
    win_counts = [r.win_count for r in res]
    lose_counts = [r.lose_count for r in res]
    trade_counts = [r.trade_count for r in res]

    out_df = pd.DataFrame(list(zip(codes,summaries, win_counts,lose_counts,trade_counts)),
                  columns=['code','summary','win_count','lose_count','trade_count'])
    out_df.to_csv('zt.csv')

code = str('002104')
strategy = st.ZTBStrategy
res =[]
dtos = [dto.BaseStrategyDto(code, str(random.random()))]
run_back_test(code,strategy,dtos,res)
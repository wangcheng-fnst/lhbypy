import random

import backtrader as bt
import pandas as pd

import data as data
import strategys as st
import dto
from backtrader_plotting import Bokeh


# 对指定股票进行指定的策略回测
def run_back_test(code, strategy, strategy_dtos, res, to_html_file=False):
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    # strategy = st.JXDTStrategy
    stock_df = data.get_online_data(code)
    if stock_df is None:
        return
    stock_df['zt'] = (stock_df['close'] - stock_df.shift(1)['close']) / stock_df.shift(1)['close'] > 0.0099
    bt_data = bt.feeds.PandasData(dataname=stock_df)
    if to_html_file:
        cerebro.addstrategy(strategy, p=strategy_dtos[0])
    else:
        cerebro.optstrategy(strategy, p=strategy_dtos)

    # Add the Data Feed to Cerebro
    cerebro.adddata(bt_data, name=code)

    # cerebro.addobserver(bt.observers.Broker)
    # cerebro.addobserver(bt.observers.Trades)
    # cerebro.addobserver(bt.observers.BuySell)
    cerebro.addobserver(bt.observers.DrawDown)
    # cerebro.addanalyzer(bt.analyzers.Returns, _name='_Returns', tann=252)

    # 设置投资金额1000.0
    cerebro.broker.setcash(10000.0)
    # 每笔交易使用固定交易量
    # cerebro.addsizer(bt.sizers.FixedSize, stake=100)
    # 设置佣金为0.0
    cerebro.broker.setcommission(commission=0.0005)

    back = cerebro.run(maxcpus=1)
    if to_html_file:
        res_to_html_file(cerebro, code)

    for p in strategy_dtos:
        if to_html_file:
            re = back[0].p.item.pop(p.get_key())
        else:
            re = back[0][0].p.item.pop(p.get_key())
        if re.trade_count > 0:
            res.append(re)


# 保存结果到html
def res_to_html_file(cerebro, code):
    filename = '../../work/' + code + ".html"

    plotconfig = {
        'r:^Broker.*': dict(
            plotlinelabels=True,
        ),
        'r:^Trades.*': dict(
            plotlinelabels=True,
        ),

    }
    b = Bokeh(style='bar', filename=filename, output_mode='save')
    cerebro.plot(b)


def res_to_file(res, name):
    codes = [r.code for r in res]
    summaries = [r.summary for r in res]
    win_counts = [r.win_count for r in res]
    lose_counts = [r.lose_count for r in res]
    trade_counts = [r.trade_count for r in res]

    out_df = pd.DataFrame(list(zip(codes, summaries, win_counts, lose_counts, trade_counts)),
                          columns=['code', 'summary', 'win_count', 'lose_count', 'trade_count'])
    out_df.to_csv('../../work/csv/'+name + '.csv')


def run_with_html(code, strategy, strategy_dtos, res):
    return run_back_test(code, strategy, strategy_dtos, res, True)


def run(code, strategy, strategy_dtos, res):
    return run_back_test(code, strategy, strategy_dtos, res, False)

import backtrader as bt
import pandas as pd
import os
from backtrader_plotting import Bokeh
from src.bt_test import analyzers

html_path = '../../work/html/'
csv_path = '../../work/csv/'
if not os.path.exists(html_path):
    os.makedirs(html_path)

if not os.path.exists(csv_path):
    os.makedirs(csv_path)
    os.makedirs(csv_path + "win/")


# 对指定股票进行指定的策略回测
def run_back_test(code, stock_df, bt_data, strategy, strategy_dtos, res, to_html_file=False):
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    if stock_df is None:
        return
    if to_html_file:
        cerebro.addstrategy(strategy, p=strategy_dtos[0])
    else:
        cerebro.optstrategy(strategy, p=strategy_dtos)

    # Add the Data Feed to Cerebro
    cerebro.adddata(bt_data, name=code)

    cerebro.addobserver(bt.observers.Broker)
    cerebro.addobserver(bt.observers.Trades)
    cerebro.addobserver(bt.observers.BuySell)
    cerebro.addobserver(bt.observers.DrawDown)
    cerebro.addobserver(bt.observers.Benchmark)
    cerebro.addanalyzer(bt.analyzers.Returns, _name='_Returns')
    cerebro.addanalyzer(bt.analyzers.TimeReturn, _name='_TimeReturn')
    cerebro.addanalyzer(analyzers.TotalValue, _name='_TotalValue')

    # 设置投资金额1000.0
    cash = strategy_dtos[0].begin_cash
    cerebro.broker.setcash(cash)
    # 每笔交易使用固定交易量
    # cerebro.addsizer(bt.sizers.FixedSize, stake=100)
    # 设置佣金为0.0
    cerebro.broker.setcommission(commission=0.0005)

    back = cerebro.run(maxcpus=1)
    # if to_html_file:
    #     res_to_html_file(cerebro, code)
    analyzer_map = {}
    for p in strategy_dtos:
        if to_html_file:
            re = back[0].p.item.pop(p.get_key())
            a_t = {p.get_key(): back[0].analyzers}
            analyzer_map.update(a_t)
        else:
            re = back[0][0].p.item.pop(p.get_key())
            a_t = {p.get_key(): back[0][0].analyzers}
            analyzer_map.update(a_t)
        if re.trade_count > 0:
            res.append(re)
    return cerebro, analyzer_map


# 保存结果到html
def res_to_html_file(cerebro, code):
    filename = html_path + code + ".html"

    plotconfig = {
        'r:^Broker.*': dict(
            plotlinelabels=True,
        ),
        'r:^Trades.*': dict(
            plotlinelabels=True,
        ),

    }
    b = Bokeh(style='line', filename=filename, output_mode='save')
    cerebro.plot(b)


def res_to_file(res, name):
    codes = [r.code for r in res]
    summaries = [r.summary for r in res]
    win_counts = [r.win_count for r in res]
    lose_counts = [r.lose_count for r in res]
    trade_counts = [r.trade_count for r in res]
    cashes = [r.begin_cash for r in res]
    values = [r.end_cash for r in res]

    out_df = pd.DataFrame(list(zip(codes, summaries, win_counts, lose_counts, trade_counts, cashes, values)),
                          columns=['code', 'summary', 'win_count', 'lose_count', 'trade_count', 'cash', 'value'])
    out_df.to_csv(csv_path + name + '.csv')

    win_file = csv_path + 'win/' + name + '.csv'
    out_df[out_df['value'] > out_df['cash']].to_csv(win_file)


def run_with_html(code, stock_df, bt_data, strategy, strategy_dtos, res):
    return run_back_test(code, stock_df, bt_data, strategy, strategy_dtos, res, True)

# 策略优化
def run_with_opt(code, stock_df, bt_data, strategy, strategy_dtos, res):
    return run_back_test(code, stock_df, bt_data, strategy, strategy_dtos, res, False)

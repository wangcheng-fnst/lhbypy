import random
import run
import dto
import strategys as st
import data
import bao_stock
import pandas as pd
import src.common.constants as constants
import strategy_result_analysis as sra
import stock_pool as sp
import  datetime

# 测试涨停板
import AddMorePandaFeed

import matplotlib as mpl

mpl.rcParams['font.family']='PingFang HK'
mpl.rcParams['axes.unicode_minus']=False

# 处理单个股票多个策略的结果，生成策略收益和基础收益曲线图
def handle_result(cerebro, strategy_dtos, analyzer_map, base_return, res):
    for strategy in strategy_dtos:
        key = strategy.get_key()
        analyzer = analyzer_map[key]
        # 策略收益序列
        pnl = pd.Series(analyzer.getbyname('_TimeReturn').get_analysis())
        plot_df = pd.DataFrame(pnl, columns=['策略收益'])
        plot_df['基础收益'] = base_return
        plot_name = constants.get_result_path() + strategy.code + strategy.name + '_plot.png'
        ax = plot_df.plot()
        for r in res:
            if r.code == strategy.code:
                ax.set_title(r.get_result_str(), fontsize=10)
                break
        fig = ax.get_figure()
        fig.savefig(plot_name)
        # 单只股票结果存库


def test_zt(stock_datas, n_code=None, model='hc'):
    res = []
    codes = [c for c in stock_datas.keys()]
    if n_code:
        codes = [n_code]
    i = 0
    for code in codes:
        try:
            i += 1
            code = str(code)
            stock_df = stock_datas.get(code)
            if stock_df is None:
                continue
            stock_df['OpenInterest'] = 0
            stock_df = stock_df[['date', 'code', 'open', 'high', 'low', 'close', 'turn', 'pe', 'pb', 'volume', 'lb']]

            strategy = st.ZTBStrategy
            dtos = [dto.BaseStrategyDto(code, '涨停策略', 100000)]
            bt_data = AddMorePandaFeed.AddMorePandaFees(dataname=stock_df)
            cerebro, analyzer_map = run.run_with_html(code, stock_df, bt_data, strategy, dtos, res)
            stock_df['base_return'] = (stock_df['close'] - stock_df.iloc[0]['close']) / stock_df.iloc[0]['close']
            print('finished %i,%s' % (i, code))

            # handle_result(cerebro, dtos, analyzer_map, stock_df['base_return'], res)
        except Exception as e:
            print('code=%s, e=%s' % (code, e))

    if model == 'hc':
        sra.handle_strategy_result(res, constants.get_result_path('ZTBStrategy/'))
    return res


def test_jx(stock_datas, n_code=None, model='hc'):
    res = []
    codes = stock_datas.keys()
    if n_code:
        codes = [n_code]
    i = 0
    for code in codes:
        try:
            i += 1
            code = str(code)
            stock_df = stock_datas.get(code)
            if stock_df is None:
                continue
            stock_df['OpenInterest'] = 0
            stock_df = stock_df[['date', 'code', 'open', 'high', 'low', 'close', 'turn', 'pe', 'pb', 'volume', 'lb']]
            strategy = st.JXDTStrategy
            bt_data = AddMorePandaFeed.AddMorePandaFees(dataname=stock_df)
            dtos = [dto.JXDto(code, 5, 10, 20, 180, '均线-1', 100000)]
            cerebro, analyzer_map = run.run_with_opt(code, stock_df, bt_data, strategy, dtos, res)
            print('finished %i,%s' % (i, code))
            # stock_df['base_return'] = (stock_df['close'] - stock_df.iloc[0]['close']) / stock_df.iloc[0]['close']
            # handle_result(cerebro, dtos, analyzer_map, stock_df['base_return'], res)
        except Exception as e:
            print('code=%s, e=%s' % (code,e))
    if model == 'hc':
        sra.handle_strategy_result(res, constants.get_result_path('JXDTStrategy/'))
    return res


def run_test(strategy):
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    stock_datas = sp.get_all('2020-01-01', today)
    if strategy == 'jx':
        test_jx(stock_datas=stock_datas)
    if strategy == 'zt':
        test_zt(stock_datas=stock_datas)

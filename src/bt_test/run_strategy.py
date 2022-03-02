import random
import run
import dto
import strategys as st
import data
import bao_stock
import pandas as pd
import constants

# 测试涨停板
from src.bt_test import AddMorePandaFeed

from pylab import mpl

mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False

# 处理单个股票多个策略的结果，生成策略收益和基础收益曲线图
def handle_result(cerebro, strategy_dtos, analyzer_map, base_return, res):
    for strategy in strategy_dtos:
        key = strategy.get_key()
        analyzer = analyzer_map[key]
        # 策略收益序列
        pnl = pd.Series(analyzer.getbyname('_TimeReturn').get_analysis())
        plot_df = pd.DataFrame(pnl, columns=['strategy_returns'])
        plot_df['base_return'] = base_return
        plot_name = constants.get_result_path() + strategy.code + strategy.name + '_plot.png'
        ax = plot_df.plot()
        ax.set_title(strategy.code)
        fig = ax.get_figure()
        fig.savefig(plot_name)
        # 单只股票结果存库


def test_zt(n_code=None):
    res = []
    codes = data.read_stock_code().loc[1000:1010]['code']
    if n_code:
        codes = [n_code]
    for code in codes:
        code = str(code)
        stock_df = bao_stock.get_k_bao_online(code)
        if stock_df is None:
            continue
        stock_df['OpenInterest'] = 0
        stock_df = stock_df[['date', 'code', 'open', 'high', 'low', 'close', 'turn', 'peTTM', 'pbMRQ']]

        strategy = st.ZTBStrategy
        dtos = [dto.BaseStrategyDto(code, str(random.randint(1, 100)), 10000)]
        bt_data = AddMorePandaFeed.AddMorePandaFees(dataname=stock_df)
        cerebro, analyzer_map = run.run_with_html(code, stock_df, bt_data, strategy, dtos, res)
        stock_df['base_return'] = (stock_df['close'] - stock_df.iloc[0]['close']) / stock_df.iloc[0]['close']
        handle_result(cerebro, dtos, analyzer_map, stock_df['base_return'], res)
    run.res_to_file(res, 'zt')


def test_jx(n_code=None):
    res = []
    codes = data.read_stock_code().loc[1000:1010]['code']
    if n_code:
        codes = [n_code]
    for code in codes:
        code = str(code)
        stock_df = bao_stock.get_k_bao_online(code)
        if stock_df is None:
            continue
        stock_df['OpenInterest'] = 0
        stock_df = stock_df[['date', 'code', 'open', 'high', 'low', 'close', 'turn', 'peTTM', 'pbMRQ']]
        strategy = st.JXDTStrategy
        dtos = [dto.JXDto(code, 5, 10, 20, 30, '均线-1', 10000)]
        bt_data = AddMorePandaFeed.AddMorePandaFees(dataname=stock_df)

        cerebro, analyzer_map = run.run_with_html(code, stock_df, bt_data, strategy, dtos, res)
        stock_df['base_return'] = (stock_df['close'] - stock_df.iloc[0]['close']) / stock_df.iloc[0]['close']
        handle_result(cerebro, dtos, analyzer_map, stock_df['base_return'], res)
    run.res_to_file(res, 'jx')


test_jx()


# test_zt()



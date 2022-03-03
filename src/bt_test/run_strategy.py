import random
import run
import dto
import strategys as st
import data
import bao_stock
import pandas as pd
import constants
import strategy_result_analysis as sra

# 测试涨停板
from src.bt_test import AddMorePandaFeed

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
    codes = data.read_stock_code()['code']
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
        bt_data = AddMorePandaFeed.AddMorePandaFees(dataname=stock_df)
        dtos = [dto.JXDto(code, 5, 10, 20, 30, '均线-1', 100000),dto.JXDto(code, 5, 20, 60, 180, '均线-2', 100000)]
        cerebro, analyzer_map = run.run_with_opt(code, stock_df, bt_data, strategy, dtos, res)
        # stock_df['base_return'] = (stock_df['close'] - stock_df.iloc[0]['close']) / stock_df.iloc[0]['close']
        # handle_result(cerebro, dtos, analyzer_map, stock_df['base_return'], res)
    sra.handle_strategy_result(res, constants.get_result_path('JXDTStrategy/'))


test_jx()


# test_zt()



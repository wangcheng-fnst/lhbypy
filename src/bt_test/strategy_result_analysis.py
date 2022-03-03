# 回测结果分析
import pandas as pd
import constants

# 处理策略在股票上效果的结果
def handle_strategy_result(res, output_file_dir):
    list = [(r.code, r.strategy_name, r.win_count, r.lose_count, r.trade_count, r.begin_cash, r.end_cash, r.summary) for
            r in res]

    out_df = pd.DataFrame(list,
                          columns=['code', 'strategy', 'win_count', 'lose_count', 'trade_count', 'cash', 'value',
                                   'summary'])
    out_df['win_rate'] = (out_df['win_count'] / out_df['trade_count'])

    # 求平均值
    deal_df = out_df.groupby('strategy').mean()
    deal_df['win_rate'] = deal_df['win_rate'].apply(lambda x: format(x, '.2%'))
    deal_df.to_csv(output_file_dir + '总览.csv')
    # top 10 排序
    top_df = out_df.sort_values(['strategy', 'value', 'win_count'], ascending=False).groupby('strategy').head(10)
    top_df.to_csv(output_file_dir + 'top10.csv')

# 处理单个股票多个策略的结果，生成策略收益和基础收益曲线图
def handle_single_result(cerebro, strategy_dtos, analyzer_map, base_return, res):
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
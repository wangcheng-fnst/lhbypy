import backtrader as bt
import data as data
import strategys as st

stock_df = data.read_data('600600',start='2021-01-01',end='2022-01-01')

bt_data = bt.feeds.PandasData(dataname=stock_df)


# Create a cerebro entity
cerebro = bt.Cerebro()

# Add a strategy
strategy = st.JXDTStrategy
# cerebro.addstrategy(strategy)

strats = cerebro.optstrategy(
        strategy,
        period=[(5,10,20,30,'jx1'),(10,20,30,40,'jx2'),(20,30,40,50,'jx3')])

# Add the Data Feed to Cerebro
cerebro.adddata(bt_data)

# 设置投资金额1000.0
cerebro.broker.setcash(100000.0)
# 每笔交易使用固定交易量
cerebro.addsizer(bt.sizers.FixedSize, stake=100)
# 设置佣金为0.0
cerebro.broker.setcommission(commission=0.0005)

cerebro.addobserver(bt.observers.Broker)
cerebro.addobserver(bt.observers.Trades)
cerebro.addobserver(bt.observers.BuySell)
cerebro.addobserver(bt.observers.DrawDown)
cerebro.addanalyzer(bt.analyzers.Returns, _name='_Returns', tann=252)

# 引擎运行前打印期出资金
print('组合期初资金: %.2f' % cerebro.broker.getvalue())

result = cerebro.run(maxcpus=1)
for r in result:
    print(r[0].p.res)
# 剩余本金
# money_left = cerebro.broker.getvalue()
#
# trade_count = result[0].trade_count
# win_count = result[0].win_count
# lose_count = result[0].lose_count

# print('交易总次数：%i，盈利次数：%i，亏损次数：%i' % (trade_count, win_count, lose_count))
# 引擎运行后打期末资金
# print('组合期末资金: %.2f, buy:%i,sell:%i' % (cerebro.broker.getvalue(),result[0].buy_count,result[0].sell_count))

# Plot the result
# cerebro.plot()



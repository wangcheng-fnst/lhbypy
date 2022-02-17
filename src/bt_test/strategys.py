import backtrader as bt
import dto as dto

# 创建策略继承bt.Strategy
# 开盘价上穿均线买入100股，开盘价下穿均线卖出全部
class TestStrategy(bt.Strategy):
    params = (
        # 均线参数设置15天，15日均线
        ('maperiod', 15),
        ('ma2', 20),
        ('ma3', 60),
        ('ma4', 240),
    )
    # 跟踪挂单
    order = None
    buy_count = 0
    sell_count = 0

    def log(self, txt, dt=None):
        # 记录策略的执行日志
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # 保存收盘价的引用
        self.dataclose = self.datas[0].close
        self.dataopen = self.datas[0].open

        # 买入价格和手续费
        self.buyprice = None
        self.buycomm = None
        # 加入均线指标
        self.sma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.maperiod)

    # 订单状态通知，买入卖出都是下单
    def notify_order(self, order):
        self.order = order
        if order.status in [order.Submitted, order.Accepted]:
            # broker 提交/接受了，买/卖订单则什么都不做
            return

        # 检查一个订单是否完成
        # 注意: 当资金不足时，broker会拒绝订单
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    '已买入, 价格: %.2f, 费用: %.2f, 股数：%i，佣金 %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.size,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
                self.buy_count += order.executed.size
            elif order.issell():
                self.log('已卖出, 价格: %.2f, 费用: %.2f, 股数：%i，佣金 %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.size,
                          order.executed.comm))
                self.sell_count += order.executed.size

            # 记录当前交易数量
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('订单取消/保证金不足/拒绝')

        # 其他状态记录为：无挂起订单
        self.order = None

    # 交易状态通知，一买一卖算交易
    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log('交易利润, 毛利润 %.2f, 净利润 %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):
        # 记录开盘价
        # self.log('Close, %.2f' % self.dataopen[0])

        # 如果有订单正在挂起，不操作
        if self.order:
            return

        # 如果没有持仓则买入
        if not self.position:
            # 今天的开盘价在均线价格之上
            if self.dataopen[0] > self.sma[0]:
                # 买入
                self.log('买入单, %.2f' % self.dataopen[0])
                    # 跟踪订单避免重复
                self.order = self.buy(size=200)
        else:
            # 如果已经持仓，开盘价在均线价格之下
            if self.dataopen[0] < self.sma[0]:
                # 全部卖出
                self.log('卖出单, %.2f' % self.dataopen[0])
                # 跟踪订单避免重复
                self.order = self.sell(size=200)



class BaseStrategy(bt.Strategy):


    def __init__(self):
        # 跟踪挂单
        self.order = None
        self.buy_count = 0
        self.sell_count = 0
        # 买入价格和手续费
        self.buyprice = None
        self.buycomm = None
        self.win_count = 0
        self.lose_count = 0
        self.trade_count = 0

    def log(self, txt, dt=None):
        # 记录策略的执行日志
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

        # 订单状态通知，买入卖出都是下单

    def notify_order(self, order):
        self.order = order
        if order.status in [order.Submitted, order.Accepted]:
            # broker 提交/接受了，买/卖订单则什么都不做
            return

        # 检查一个订单是否完成
        # 注意: 当资金不足时，broker会拒绝订单
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    '已买入, 价格: %.2f, 费用: %.2f, 股数：%i，佣金 %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.size,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
                self.buy_count += order.executed.size
            elif order.issell():
                self.log('已卖出, 价格: %.2f, 费用: %.2f, 股数：%i，佣金 %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.size,
                          order.executed.comm))
                self.sell_count += order.executed.size

            # 记录当前交易数量
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('订单取消/保证金不足/拒绝')

        # 其他状态记录为：无挂起订单
        self.order = None

        # 交易状态通知，一买一卖算交易

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.trade_count += 1;
        if trade.pnlcomm > 0:
            self.win_count += 1
        else:
            self.lose_count += 1
        self.log('交易利润, 毛利润 %.2f, 净利润 %.2f' %
                 (trade.pnl, trade.pnlcomm))

# 均线多头策略
class JXDTStrategy(BaseStrategy):

    params = dict(
        period = (5, 10,20,30,'jx'),
        res=None
    )

    def __init__(self):

        self.dataclose = self.datas[0].close
        self.dataopen = self.datas[0].open
        self.ma1 = bt.talib.SMA(self.dataclose, timeperiod=self.params.period[0])
        self.ma2 = bt.talib.SMA(self.dataclose, timeperiod=self.params.period[1])
        self.ma3 = bt.talib.SMA(self.dataclose, timeperiod=self.params.period[2])
        self.ma4 = bt.talib.SMA(self.dataclose, timeperiod=self.params.period[3])
        self.name = self.params.period[4]
        self.result = None
        BaseStrategy.__init__(self)


    def stop(self):
        self.result = '策略：%s,最后资金：%.2f，交易总次数：%i，盈利次数：%i，亏损次数：%i' % (self.name, self.broker.getvalue(), self.trade_count, self.win_count, self.lose_count)
        self.params.res = self.result
        # print('策略：%s,最后资金：%.2f，交易总次数：%i，盈利次数：%i，亏损次数：%i' % (self.name, self.broker.getvalue(), self.trade_count, self.win_count, self.lose_count))

    def next(self):
        # 如果有订单正在挂起，不操作
        if self.order:
            return

        # 如果没有持仓则买入
        if not self.position:
            # 今天的开盘价在均线价格之上
            if self.ma1[0] >= self.ma2[0] and self.ma2[0] >= self.ma3[0] and self.ma3[0] >= self.ma4[0]:
                # 买入
                self.log('买入单, %.2f' % self.dataopen[0])
                # 跟踪订单避免重复
                self.order = self.buy(size=200)
        else:
            # 如果已经持仓，开盘价在ma1均线价格之下
            if self.dataopen[0] < self.ma1[0]:
                # 全部卖出
                self.log('卖出单, %.2f' % self.dataopen[0])
                # 跟踪订单避免重复
                self.order = self.sell(size=200)



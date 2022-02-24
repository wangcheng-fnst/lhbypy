import backtrader as bt
import dto as dto
import talib as ta
import datetime

# 订单的首个交易日在下一个k线上
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
        p=dto.JXDto('600600', 5, 10, 20, 30, 'jx'),

        item={}
    )

    def __init__(self):

        self.dataclose = self.datas[0].close
        self.dataopen = self.datas[0].open
        self.ma1 = bt.talib.SMA(self.dataclose, timeperiod=self.params.p.ma1)
        self.ma2 = bt.talib.SMA(self.dataclose, timeperiod=self.params.p.ma2)
        self.ma3 = bt.talib.SMA(self.dataclose, timeperiod=self.params.p.ma3)
        self.ma4 = bt.talib.SMA(self.dataclose, timeperiod=self.params.p.ma4)
        self.name = self.params.p.name
        self.result = None
        BaseStrategy.__init__(self)

    def stop(self):
        self.result = '股票：%s, 策略：%s,最后资金：%.2f，交易总次数：%i，盈利次数：%i，亏损次数：%i' % (
            self.params.p.code, self.name, self.broker.getvalue(), self.trade_count, self.win_count, self.lose_count)
        # self.params.res = self.result

        res = dto.BtResultDto(self.params.p.code, self.result, self.win_count, self.lose_count)
        self.params.item.update({self.params.p.get_key(): res})

    def next(self):
        # 如果有订单正在挂起，不操作
        if self.order:
            return

        # 如果没有持仓则买入
        if not self.position:
            # 均线多头
            if self.ma1[0] >= self.ma2[0] and self.ma2[0] >= self.ma3[0] and self.ma3[0] >= self.ma4[0]:
                # 买入
                # self.log('买入单, %.2f' % self.dataopen[0])
                # 跟踪订单避免重复
                self.order = self.buy(size=200)
        else:
            # 如果已经持仓，开盘价在ma1均线价格之下
            if self.dataopen[0] < self.ma1[-1]:
                # 全部卖出
                # self.log('卖出单, %.2f' % self.dataopen[0])
                # 跟踪订单避免重复
                self.order = self.sell(size=200)

    @staticmethod
    def judge_stock(stock_data, p):
        stock_data['ma1'] = ta.SMA(stock_data['close'], timeperiod=p.ma1)
        stock_data['ma2'] = ta.SMA(stock_data['close'], timeperiod=p.ma2)
        stock_data['ma3'] = ta.SMA(stock_data['close'], timeperiod=p.ma3)
        stock_data['ma4'] = ta.SMA(stock_data['close'], timeperiod=p.ma4)
        hit = (stock_data['ma1'][-1] >= stock_data['ma2'][-1]) \
              and (stock_data['ma2'][-1] >= stock_data['ma3'][-1]) \
              and (stock_data['ma3'][-1] >= stock_data['ma4'][-1])
        print('code=%s,hti=%s,ma1=%.2f,ma2=%.2f,ma3=%.2f,ma4=%.2f' % (stock_data['code'][-1], hit,stock_data['ma1'][-1],
                                                                   stock_data['ma2'][-1], stock_data['ma3'][-1],
                                                                   stock_data['ma4'][-1]))
        return hit


# 涨停板策略连续n天涨停后买入，买入后开板就卖出
class ZTBStrategy(BaseStrategy):
    params = dict(
        p=dto.BaseStrategyDto('600600','zt-1'),
        n=2,
        stock_data=None,
        item={}
    )
    def __init__(self):
        BaseStrategy.__init__(self)
        self.result = None
        self.cash = None
        self.end_date = self.data0.datetime.date(-1)
        # self.zt = s

    def notify_cashvalue(self, cash, value):
        self.cash = cash
        # if (cash != value):
        #     self.log('cash=%.2f,value=%.2f' % (cash, value))

    def stop(self):
        self.result = '股票：%s, 策略：%s,最后资金：%.2f，交易总次数：%i，盈利次数：%i，亏损次数：%i' % (
            self.params.p.code, self.p.p.name, self.broker.getvalue(), self.trade_count, self.win_count, self.lose_count)
        # self.params.res = self.result

        res = dto.BtResultDto(self.params.p.code, self.result, self.win_count, self.lose_count, self.trade_count)
        self.params.item.update({self.params.p.get_key(): res})

    def next(self):
        # 0 回测对当前时间,
        # -1 回测对当前时间对前一天 （如果回测对当前时间是第一个数据，-1 表示回测时间的最后一天，因为会形成一个环）
        # 1 回测对当前时间的后一天
        cur_date = self.data0.datetime.date(0)
        if cur_date >= self.end_date:
            return
        # 明天是否一字板涨停
        can = (self.data0.open[1] - self.data0.close[1]) / self.data0.close[1] < 0.09
        # if cur_date > datetime.date(year=2022,month=2,day=14):
        #     self.log('run')
        # 如果有订单正在挂起，不操作
        if self.order:
            return

        # 如果没有持仓则买入
        if not self.position:
            # 连续n天涨停(包含今天)，明天开盘买入
            # 判断明天是否可以买入
            flag = False

            for i in range(1, self.p.n+1):
                pre_date = self.data0.datetime.date(0 - i)
                pp_date = self.data0.datetime.date(0 - i - 1)
                if cur_date > pre_date > pp_date:
                    flag = (self.data0.close[0] - self.data0.close[0 - i])/self.data0.close[0 - i] >= 0.099
                    if not flag:
                        break
            # 达到条件了，并且不是一字涨停可以买入了

            if flag and can:
                    # 不是一字涨停，高于开盘价0.01 买入
                    cash = self.broker.getcash()
                    buy_price = self.datas[0].open[1]+0.01
                    size = int((cash - cash * 0.0005) / buy_price/100) * 100
                    # 跟踪订单避免重复
                    self.order = self.buy(data=self.data0,size=size, price=buy_price,exectype=bt.Order.Market)
                    self.log('买入单, %.2f,前天价格：c=%.2f,当前现金:%.2f,买价:%.2f，股数:%.2f' % (
                            buy_price, self.datas[0].close[-1], cash, buy_price, size))

        else:
            # 今天没有一字板,  卖

            if (self.data0.open[1] - self.data0.close[1]) / self.data0.close[1] < 0.09:
                sell_price = self.datas[0].open[0] - 0.01
                self.log('现金：%.2f' % self.broker.getcash())
                self.log('卖出单, %.2f' % sell_price)
                # 跟踪订单避免重复
                self.order = self.sell(size=self.position.size, price=sell_price)






# 启明星形态策略

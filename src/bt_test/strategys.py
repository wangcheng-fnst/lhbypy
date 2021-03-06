import backtrader as bt
import src.bt_test.dto as dto
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
        # 基本技术指标：成交量，换手，量比
        self.volume_ma5 = bt.talib.SMA(self.datas[0].volume, timeperiod=5)
        self.turn_ma5 = bt.talib.SMA(self.datas[0].turn, timeperiod=5)
        # 跟踪挂单
        self.order = None
        self.buy_count = 0
        self.sell_count = 0
        # 买入价格和手续费
        self.buydate = None
        self.buyprice = None
        self.buycomm = None
        self.win_count = 0
        self.lose_count = 0
        self.trade_count = 0
        # 结果
        self.result = None
        self.trade_detail = {}

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
                self.buydate = self.datas[0].datetime.date(0)
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
                self.buy_count += order.executed.size
                trade_detail = {}
                trade_detail.update({'volume': self.datas[0].volume[0]})
                trade_detail.update({'volume_ma5': self.volume_ma5[0]})
                trade_detail.update({'turn': self.datas[0].turn[0]})
                trade_detail.update({'turn_ma5': self.turn_ma5[0]})

                self.trade_detail.update({self.datas[0].datetime.date(0): trade_detail})

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
        trade_detail = self.trade_detail.get(self.buydate)
        trade_detail.update({'pnl': trade.pnlcomm})

    def stop(self):
        self.result = '股票：%s, 策略：%s,最后资金：%.2f，交易总次数：%i，盈利次数：%i，亏损次数：%i' % (
            self.params.p.code, self.p.p.name, self.broker.getvalue(), self.trade_count, self.win_count, self.lose_count)
        # self.params.res = self.result

        res = dto.BtResultDto(self.params.p.code, self.result, self.win_count, self.lose_count,
                              self.trade_count, self.p.p.begin_cash, self.broker.getvalue(), self.p.p.name, self.trade_detail)
        self.params.item.update({self.params.p.get_key(): res})



# 均线多头策略，次日开盘价买入
class JXDTStrategy(BaseStrategy):
    params = dict(
        p=dto.JXDto('600600', 5, 10, 20, 30, 'jx', 10000),

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
        self.end_date = self.data0.datetime.date(-1)

        BaseStrategy.__init__(self)


    def next(self):
        cur_date = self.data0.datetime.date(0)
        if cur_date >= self.end_date:
            return
        total = len(self.datas[0].open.array)
        idx = self.datas[0].open.idx
        if idx >= (total - 1):
            self.log('to today no tomorrow')
            return
        # 如果有订单正在挂起，不操作
        if self.order:
            return

        # 如果没有持仓则买入
        if not self.position:
            # 均线多头
            if self.ma1[0] >= self.ma2[0] and self.ma2[0] >= self.ma3[0] \
                    and self.ma1[-1] >= self.ma2[-1] and self.ma2[-1] >= self.ma3[-1] :
                cash = self.broker.getcash()
                buy_price = self.datas[0].open[1] + 0.01
                size = int((cash - cash * 0.0005) / buy_price / 100) * 100
                # 跟踪订单避免重复
                self.order = self.buy(data=self.data0, size=size, price=buy_price, exectype=bt.Order.Market)
                # 买入
                self.log('买入单, %.2f' % buy_price)
                # 跟踪订单避免重复
        else:
            # 如果已经持仓，如果收盘价在ma2均线价格之下，且还是盈利 或者持仓达到了10日
            yl_flag = self.buyprice < self.dataclose[0] and self.dataclose[0] < self.ma2[0]
            cur_date = self.data0.datetime.date(0)
            hold_date = (cur_date - self.buydate).days
            if yl_flag or hold_date >= 10:
                sell_price = self.datas[0].open[1] - 0.01
                self.log('卖出单, %.2f' % sell_price)
                # 跟踪订单避免重复
                self.order = self.sell(size=self.position.size, price=sell_price)


    @staticmethod
    def judge_stock(stock_data, p):
        stock_data['ma1'] = ta.SMA(stock_data['close'], timeperiod=p.ma1)
        stock_data['ma2'] = ta.SMA(stock_data['close'], timeperiod=p.ma2)
        stock_data['ma3'] = ta.SMA(stock_data['close'], timeperiod=p.ma3)
        stock_data['ma4'] = ta.SMA(stock_data['close'], timeperiod=p.ma4)
        hit = (stock_data['ma1'][-1] >= stock_data['ma2'][-1]) \
              and (stock_data['ma2'][-1] >= stock_data['ma3'][-1])  \
              and (stock_data['ma2'][-2] >= stock_data['ma3'][-2]) \
              and (stock_data['ma2'][-2] >= stock_data['ma3'][-2])

        return hit


# 涨停板策略连续n天涨停后买入，买入后开板就卖出
# n = 2: 昨天和今天都涨停，明天如果不是一字板，开盘买入， 后天如果不是一字板，则卖出
# todo：均线多头加涨停，第二天追
class ZTBStrategy(BaseStrategy):
    params = dict(
        p=dto.BaseStrategyDto('600600','zt-1',10000),
        n=2,
        stock_data=None,
        item={}
    )
    def __init__(self):
        BaseStrategy.__init__(self)

        self.cash = None
        self.end_date = self.data0.datetime.date(-1)
        self.dataclose = self.datas[0].close
        self.dataopen = self.datas[0].open
        self.ma1 = bt.talib.SMA(self.dataclose, timeperiod=5)
        self.ma2 = bt.talib.SMA(self.dataclose, timeperiod=10)
        self.ma3 = bt.talib.SMA(self.dataclose, timeperiod=20)
        self.ma4 = bt.talib.SMA(self.dataclose, timeperiod=30)
        # self.zt = s

    def notify_cashvalue(self, cash, value):
        self.cash = cash


    def jxdt_judge(self):
        flag = (self.ma1[0] >= self.ma2[0]) and (self.ma2[0] >= self.ma3[0]) \
                    and (self.ma1[-1] >= self.ma2[-1]) and (self.ma2[-1] >= self.ma3[-1])
        return flag


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
                pre_index = 0 - i
                pp_index = 0 - i - 1
                pre_date = self.data0.datetime.date(pre_index)
                pp_date = self.data0.datetime.date(pp_index)
                if cur_date > pre_date > pp_date:
                    flag = (self.data0.close[1 - i] - self.data0.close[0 - i])/self.data0.close[0 - i] >= 0.099
                    if not flag:
                        break
            # 达到条件了，并且不是一字涨停可以买入了

            # 均线多头
            if not self.jxdt_judge():
                return

            if flag and can:
                    # 不是一字涨停，高于开盘价0.01 买入
                    cash = self.broker.getcash()
                    buy_price = self.datas[0].open[1]+0.01
                    size = int((cash - cash * 0.0005) / buy_price/100) * 100
                    # 跟踪订单避免重复
                    self.order = self.buy(data=self.data0,size=size, price=buy_price,exectype=bt.Order.Market)
                    self.log('买入单, %.2f,前天的价格：%.2f,昨天价格：%.2f,今天的价格：%.2f,当前现金:%.2f,买价:%.2f，股数:%.2f' % (
                            buy_price, self.datas[0].close[-2],self.datas[0].close[-1], self.datas[0].close[0], cash, buy_price, size))

        else:
            # 天没有一字板,  卖

            if (self.data0.open[1] - self.data0.close[1]) / self.data0.close[1] < 0.09:
                sell_price = self.datas[0].open[1] - 0.01
                self.log('现金：%.2f' % self.broker.getcash())
                self.log('卖出单, %.2f' % sell_price)
                # 跟踪订单避免重复
                self.order = self.sell(size=self.position.size, price=sell_price)






# 启明星形态策略

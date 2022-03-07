import constants

class BaseStrategyDto:
    def __init__(self, code, name, begin_cash):
        self.code = code
        self.name = name
        self.begin_cash = begin_cash

    def get_key(self):
        return self.code+"-"+self.name

class JXDto(BaseStrategyDto):
    def __init__(self,code,ma1, ma2, ma3, ma4, name, cash):
        BaseStrategyDto.__init__(self, code, name, cash)
        self.ma1 = ma1
        self.ma2 = ma2
        self.ma3 = ma3
        self.ma4 = ma4


    # def get_key(self):
    #     return self.code+"-"+self.name


class BtResultDto(object):
    def __init__(self,code,summary,win_count,lose_count, trade_count,
                 begin_cash, end_cash, strategy_name, trade_detail):
        self.code = code
        self.summary = summary
        self.win_count = win_count
        self.lose_count = lose_count
        self.trade_count = trade_count
        self.begin_cash = begin_cash
        self.end_cash = end_cash
        self.strategy_name = strategy_name
        self.trade_detail = trade_detail

    def get_result_str(self):
        return '股票：%s, 策略：%s\n初始资金：%.2f，最后资金：%.2f \n盈利次数：%i，亏损次数：%i' % (self.code,self.strategy_name,self.begin_cash,
                                                                 self.end_cash,self.win_count,self.lose_count)


    def __str__(self):
        return self.summary


    def getPlotFile(self):
        dir = constants.result_path
        return dir + self.code + '_plot.png'

    def getHtmlFile(self):
        pass
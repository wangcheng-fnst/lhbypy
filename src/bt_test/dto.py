
class BaseStrategyDto:
    def __init__(self, code, name):
        self.code = code
        self.name = name

    def get_key(self):
        return self.code+"-"+self.name

class JXDto(BaseStrategyDto):
    def __init__(self,code,ma1, ma2, ma3, ma4, name):
        BaseStrategyDto.__init__(self, code, name)
        self.ma1 = ma1
        self.ma2 = ma2
        self.ma3 = ma3
        self.ma4 = ma4


    # def get_key(self):
    #     return self.code+"-"+self.name


class BtResultDto(object):
    def __init__(self,code,summary,win_count,lose_count, trade_count):
        self.code = code
        self.summary = summary
        self.win_count = win_count
        self.lose_count = lose_count
        self.trade_count = trade_count


    def __str__(self):
        return self.summary
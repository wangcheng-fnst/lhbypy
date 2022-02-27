#pandas的数据格式
from backtrader.feeds import PandasData

'''
扩展数据如换手率
'''
class AddMorePandaFees(PandasData):
    lines = ('turn', 'peTTM', 'pbMRQ',)
    params = (('turn', -1), ('peTTM', -1), ('pbMRQ', -1),)

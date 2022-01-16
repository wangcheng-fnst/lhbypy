import common.base as b
import talib as ta
import pyfolio as pf

def adx_strategy(df,ma1=13,ma2=55,ma3=89,adx=25):
    #计算MACD和ADX指标
    df['EMA1'] = ta.EMA(df.close,ma1)
    df['EMA2'] = ta.EMA(df.close,ma2)
    df['EMA3'] = ta.EMA(df.close,ma3)
    df['MACD'],df['MACDSignal'],df['MACDHist'] = ta.MACD(df.close,12,26,9)
    df['ADX'] = ta.ADX(df.high,df.low,df.close,14)
    #设计买卖信号:21日均线大于42日均线且42日均线大于63日均线;ADX大于前值小于25；MACD大于前值
    df['Buy_Sig'] =(df['EMA1']>df['EMA2'])&(df['EMA2']>df['EMA3'])&(df['ADX']<=adx)\
                    &(df['ADX']>df['ADX'].shift(1))&(df['MACDHist']>df['MACDHist'].shift(1))
    df.loc[df.Buy_Sig,'Buy_Trade'] = 1
    df.loc[df.Buy_Trade.shift(1)==1,'Buy_Trade'] = " "
    #避免最后三天内出现交易
    df.Buy_Trade.iloc[-3:]  = " " 
    df.loc[df.Buy_Trade==1,'Buy_Price'] = df.close
    df.Buy_Price = df.Buy_Price.ffill()
    df['Buy_Daily_Return']= (df.close - df.Buy_Price)/df.Buy_Price
    df.loc[df.Buy_Trade.shift(3)==1,'Sell_Trade'] = -1
    df.loc[df.Sell_Trade==-1,'Buy_Total_Return'] = df.Buy_Daily_Return
    df.loc[(df.Sell_Trade==-1)&(df.Buy_Daily_Return==0),'Buy_Total_Return'] = \
                                (df.Buy_Price - df.Buy_Price.shift(1))/df.Buy_Price.shift(1)
    df.loc[(df.Sell_Trade==-1)&(df.Buy_Trade.shift(1)==1),'Buy_Total_Return'] = \
                                (df.close-df.Buy_Price.shift(2))/df.Buy_Price.shift(2)
    #返回策略的日收益率
    return df.Buy_Total_Return.fillna(0)

def get_data_from_db(code):
    data=b.pd.read_sql(f"select * from stock_k_data where code='{code}'",b.engine)
    return data;

df = adx_strategy(df=get_data_from_db('600320'))
pf.create_simple_tear_sheet(df.tz_localize('UTC'))
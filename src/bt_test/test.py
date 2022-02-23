import pandas as pd
import dto


res = []
for i in range(1,10):
    res.append(dto.BtResultDto(i,i,i,i,i))
out_df = pd.DataFrame(columns=['code','summary','win_count','lose_count','trade_count'])

codes = [r.code for r in res]
summaries = [r.summary for r in res]
win_counts = [r.win_count for r in res]
lose_counts = [r.lose_count for r in res]
trade_counts = [r.trade_count for r in res]

df = pd.DataFrame(list(zip(codes,summaries, win_counts,lose_counts,trade_counts)),
                  columns=['code','summary','win_count','lose_count','trade_count'])
print(df)

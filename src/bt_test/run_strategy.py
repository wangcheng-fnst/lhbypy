import random
import run
import dto
import strategys as st
import data
import bao_stock



# 测试涨停板
def test_zt(n_code=None):
    res = []
    codes = data.read_stock_code().loc[1000:1010]['code']
    if n_code:
        codes = [n_code]
    for code in codes:
        code = str(code)
        stock_df = bao_stock.get_k_bao_online(code)
        if stock_df is None:
            continue
        stock_df['OpenInterest'] = 0
        stock_df = stock_df[['date','code','open','high','low','close','turn','peTTM','pbMRQ']]
        strategy = st.ZTBStrategy
        dtos = [dto.BaseStrategyDto(code, str(random.randint(1, 100)), 10000)]
        run.run_with_html(code, stock_df,strategy, dtos, res)
    run.res_to_file(res, 'zt')

test_zt()
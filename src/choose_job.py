import datetime

import src.bt_test.stock_choose as sc
from src.bt_test import strategys, dto

today = datetime.datetime.now().strftime('%Y-%m-%d')
sc.choose_stock(strategys.JXDTStrategy,
                dto.JXDto('', 5, 10, 20, 180, '均线-1', 100000),
                today)

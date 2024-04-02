from sqlite_storage import BasicStorage
from slingshot.api.jqka.breadth import breadth_intraday
from slingshot.api.jqka.hot import get_hot_intraday
from slingshot.api.jqka.industry import ind_stock_list, get_ind_list
from slingshot.api.jqka.limits import daily_limits, daily_limits_hot, daily_cont

for api in [breadth_intraday, get_hot_intraday, get_ind_list, daily_limits, daily_limits_hot, daily_cont]:
    print(f'开始{api.__name__}的存储！')
    api_storage = BasicStorage(db_path=f'../database/{api.__name__}.db', api_func=api)
    api_storage.start_storage_process()

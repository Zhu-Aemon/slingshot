import pandas as pd
import sqlite3
import datetime
from api.em.calendar import trading_days
from errors.ParamsError import ParamsError


class BasicStorage:
    """
    采取基础的Sqlite数据库作为存储数据的方式
    """

    def __init__(self, db_path, api_func):
        # 检查输入参数是否合法
        api_func_list = ['daily_limits', 'daily_limits_hot', 'daily_cont', 'breadth_live', 'breadth_intraday',
                         'ind_stock_list', 'get_ind_list', 'ind_index_data', 'get_hot_intraday', 'xq_intraday',
                         'xq_trades', 'xq_snapshot', 'xq_kline']
        if api_func.__name__ not in api_func_list:
            raise ParamsError(
                message=f'输入的api_func参数错误，输入的参数是{api_func}，允许的api函数有{", ".join(api_func_list)}')
        self.db_path = db_path
        self.__conn = sqlite3.connect(self.db_path)
        self.__cursor = self.__conn.cursor()
        self.__tables = [x[0] for x in
                         self.__cursor.execute("""SELECT name FROM sqlite_master WHERE type='table';""").fetchall()]
        self.api = api_func
        self.__update_date_range = []  # 如果是live模式为False，也就是采用历史获取的方式

        # 根据传入的api函数判断采取哪一种存储模式，究竟是所有的数据存储在database中的一张表里还是分开来按照日期存储在不同表里
        # compact - 存储在一张表里面，detail - 存储在不同的表里面
        # detail存储的时候每张表的标题例如T20240322，compact模式存储的时候，每一条记录带上时间
        mode_dict = {'daily_limits': 'detail', 'daily_limits_hot': 'detail', 'daily_cont': 'compact',
                     'breadth_live': 'detail', 'breadth_intraday': 'detail', 'ind_stock_list': 'detail',
                     'get_ind_list': 'detail', 'ind_index_data': 'compact', 'get_hot_intraday': 'detail',
                     'xq_intraday': 'detail', 'xq_trades': 'detail', 'xq_snapshot': 'detail', 'xq_kline': 'compact'}
        live_dict = {'daily_limits': False, 'daily_limits_hot': False, 'daily_cont': False,
                     'breadth_live': True, 'breadth_intraday': False, 'ind_stock_list': False,
                     'get_ind_list': False, 'ind_index_data': False, 'get_hot_intraday': False,
                     'xq_intraday': False, 'xq_trades': True, 'xq_snapshot': True, 'xq_kline': False}
        self.mode = mode_dict[self.api.__name__]
        self.live = live_dict[self.api.__name__]
        self.__init_db()
        self.__adjust_date_range()

    def __init_db(self):
        """
        初始化数据库，主要威了获取存储的时间范围
        :return: None
        """
        if self.mode == 'detail':
            # 如果采用detail存储的方式，那么要看一下所给数据库有没有被初始化，如果有，最新的表格对应什么日期
            if not self.live:  # 如果不是实时存储数据的话，那就采用历史获取数据的模式
                if len(self.__tables) > 0:  # 如果指定数据库中已经存在了数据表格
                    table_ref = [x.lstrip('T') for x in self.__tables]
                    try:
                        table_ref = [datetime.datetime.strptime(x, '%Y%m%d') for x in table_ref]  # 转换为日期格式，看下最新日期
                    except ValueError:
                        print(f'原有数据库表名称不符合格式要求！格式要求T%Y%m%d，现在得到的表名称列表是：{table_ref}')
                    latest_date = max(table_ref)
                    self.__update_date_range = trading_days(
                        start_date=datetime.datetime.strftime(latest_date, '%Y%m%d'))
                    # 检查一下现在的时间，如果现在是交易日并且现在并且处于开盘时间，那么就不要更新今天的数据
                    now_time = datetime.datetime.now()
                    if ((now_time.day == latest_date.day) and (now_time.month == latest_date.month) and
                            (now_time.year == latest_date.year) and (now_time.hour <= 15)):
                        self.__update_date_range.remove(datetime.datetime.strftime(latest_date, '%Y%m%d'))
                else:
                    self.__update_date_range = trading_days('20150101')  # 默认从20150101开始存储数据

    def start_storage_process(self):
        self.__storage_daily()

    def __adjust_date_range(self):
        """
        将初始化数据库的时候计算得到的日期范围根据每个接口的调用范围进行裁切
        ok: 20230320开始 - 涨停板数据，daily_limits, daily_limits_hot, daily_cont
        ok: 近十日 - 热榜分时，get_hot_intraday
        ok: 20230103开始 - breadth_intraday
        Todo: 最近五日（5d），最近一日（1d） - xq_intraday
        Todo: k线根数还没搞清楚 - xq_kline
        :return: None
        """
        adjusted_range = [datetime.datetime.strptime(x, '%Y%m%d') for x in self.__update_date_range]
        if self.api.__name__ in ['get_hot_intraday']:
            valid_start_date = datetime.datetime.now() - datetime.timedelta(days=10)
            valid_start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        elif self.api.__name__ in ['daily_limits', 'daily_limits_hot', 'daily_cont']:
            valid_start_date = datetime.datetime(2023, 3, 20)
        elif self.api.__name__ in ['breadth_intraday']:
            valid_start_date = datetime.datetime(2023, 1, 3)
        adjusted_range = [x for x in adjusted_range if x >= valid_start_date]
        self.__update_date_range = [datetime.datetime.strftime(x, '%Y%m%d') for x in adjusted_range]

    def __storage_daily(self):
        """
        对所有采取日频存储方式的标的，调用这个函数，这种情况假设self.api只接受date作为参数
        :return: None
        """
        for date in self.__update_date_range:
            data_iter = self.api(date=date)
            data_iter.to_sql(con=self.__conn, name=f'T{date}', if_exists='replace', index=False)

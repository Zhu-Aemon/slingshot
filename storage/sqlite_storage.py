import datetime
import sqlite3

import pandas as pd

from api.em.calendar import trading_days
from errors.ParamsError import ParamsError


class BasicStorage:
    """
    使用Sqlite数据库存储数据。
    """

    def __init__(self, db_path, api_func):
        self._validate_api_func(api_func)
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.tables = [x[0] for x in self.cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table';").fetchall()]
        self.api = api_func
        self.update_date_range = []
        self.mode, self.live = self._get_storage_mode(api_func)
        self._init_db()
        self._adjust_date_range()

    @staticmethod
    def _validate_api_func(api_func):
        valid_funcs = ['daily_limits', 'daily_limits_hot', 'daily_cont', 'breadth_live', 'breadth_intraday',
                       'ind_stock_list', 'get_ind_list', 'ind_index_data', 'get_hot_intraday', 'xq_intraday',
                       'xq_trades', 'xq_snapshot', 'xq_kline']
        if api_func.__name__ not in valid_funcs:
            raise ParamsError(
                f'Invalid api_func parameter: {api_func}. Allowed functions are: {", ".join(valid_funcs)}')

    @staticmethod
    def _get_storage_mode(api_func):
        mode_dict = {
            'daily_limits': 'detail', 'daily_limits_hot': 'detail', 'daily_cont': 'compact',
            'breadth_live': 'detail', 'breadth_intraday': 'detail', 'ind_stock_list': 'detail',
            'get_ind_list': 'detail', 'ind_index_data': 'compact', 'get_hot_intraday': 'detail',
            'xq_intraday': 'detail', 'xq_trades': 'detail', 'xq_snapshot': 'detail', 'xq_kline': 'compact'
        }
        live_dict = {
            'daily_limits': False, 'daily_limits_hot': False, 'daily_cont': False, 'breadth_live': True,
            'breadth_intraday': False, 'ind_stock_list': False, 'get_ind_list': False, 'ind_index_data': False,
            'get_hot_intraday': False, 'xq_intraday': False, 'xq_trades': True, 'xq_snapshot': True, 'xq_kline': False
        }
        return mode_dict[api_func.__name__], live_dict[api_func.__name__]

    def _init_db(self):
        if not self.live:
            self._setup_daily_mode()

    def _setup_daily_mode(self):
        if self.mode == 'detail':
            table_dates = [x.lstrip('T') for x in self.tables]
            try:
                table_dates = [datetime.datetime.strptime(x, '%Y%m%d') for x in table_dates]
            except ValueError:
                print(f'Table names in the database do not follow the required format T%Y%m%d. Found: {table_dates}')
                return
            try:
                latest_date = max(table_dates)
            except ValueError:
                latest_date = None
        elif self.mode == 'compact':
            try:
                # noinspection SqlResolve
                table_dates = [x[0] for x in self.cursor.execute("SELECT date FROM compact").fetchall()]
                table_dates = [datetime.datetime.strptime(x, "%Y-%m-%d %H:%M:%S") for x in table_dates]
                latest_date = max(table_dates)
            except (ValueError, sqlite3.OperationalError):
                latest_date = None
        print(latest_date.date(), datetime.datetime.now().date())
        if latest_date:
            self.update_date_range = trading_days(
                start_date=datetime.datetime.strftime(latest_date + datetime.timedelta(days=1), '%Y%m%d'))
            self.update_date_range = [x for x in self.update_date_range if
                                      datetime.datetime.strptime(x, '%Y%m%d').date() <= datetime.datetime.now().date()]
            if latest_date.date() == datetime.datetime.now().date():
                self.update_date_range = []
        else:
            self.update_date_range = trading_days('20150101')
            self.update_date_range = [x for x in self.update_date_range if
                                      datetime.datetime.strptime(x, '%Y%m%d').date() <= datetime.datetime.now().date()]
        if (not latest_date) and (
                datetime.datetime.now().date() == datetime.datetime.strptime(self.update_date_range[-1],
                                                                             '%Y%m%d').date()
                and datetime.datetime.now().hour <= 15):
            self.update_date_range.pop(0)

    def _adjust_date_range(self):
        adjusted_range = [datetime.datetime.strptime(x, '%Y%m%d') for x in self.update_date_range]
        if self.api.__name__ in ['get_hot_intraday']:
            valid_start_date = datetime.datetime.now() - datetime.timedelta(days=10)
        elif self.api.__name__ in ['daily_limits', 'daily_limits_hot', 'daily_cont']:
            valid_start_date = datetime.datetime(2023, 3, 20)
        elif self.api.__name__ in ['breadth_intraday']:
            valid_start_date = datetime.datetime(2023, 1, 3)
        else:
            return
        self.update_date_range = [
            x.strftime('%Y%m%d') for x in adjusted_range if x >= valid_start_date
        ]

    def start_storage_process(self):
        if not self.live:
            self._storage_daily()

    def _storage_daily(self):
        if self.mode == 'detail':
            for date in self.update_date_range:
                try:
                    data_iter = self.api(date=date)
                    data_iter.to_sql(name=f'T{date}', con=self.conn, if_exists='replace', index=False)
                except KeyError as e:
                    print(f'[{date}] KeyError: {e}')
        elif self.mode == 'compact':
            result = []
            for date in self.update_date_range:
                try:
                    data_iter = self.api(date=date)
                    result.append(data_iter)
                except KeyError as e:
                    print(f'[{date}] KeyError: {e}')
            result = pd.concat(result)
            result.to_sql(con=self.conn, name='compact', if_exists='append', index=False)

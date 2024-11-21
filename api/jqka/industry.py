"""
Created on 2024.3.24
获取同花顺行业（传统行业、概念板块、地域板块）每天的涨跌和各成分股
"""
import requests
import datetime
import random

import pandas as pd

from concurrent.futures import ThreadPoolExecutor, as_completed

headers = {
    "Host": "dq.10jqka.com.cn",
    "Accept": "application/json, text/plain, */*",
    "Sec-Fetch-Site": "cross-site",
    "Accept-Language": "zh-CN,zh-Hans;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Sec-Fetch-Mode": "cors",
    "Content-Type": "application/json",
    "Origin": "https://localhost:8088",
    "User-Agent": f"Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Safari/604.1 Falcon/0.3.29 userid/{random.randint(710000000, 712680385)}",
    "Referer": "https://localhost:8088/",
    "Connection": "keep-alive"
}


def ind_stock_list(ind_code, date):
    """
    获取一个板块对应的股票列表和涨跌，指定日期
    :param ind_code: 板块代码，同花顺定义的
    :param date: 想获取哪一天的，请传入字符串，例如20240322
    :return: DataFrame，内容是各成分股和涨跌
    """
    url = "https://dq.10jqka.com.cn/interval_calculation/stock_info/v1/get_stock_list_by_block"
    payload = {
        "block_code": f"{ind_code}",
        "sort_info": {
            "sort_field": "0",
            "sort_type": "desc"
        },
        "history_info": {
            "history_type": "1",
            "end_date": f"{date}000000",
            "start_date": f"{date}000000"
        },
        "page_info": {
            "page_size": 20,
            "page": 1
        },
        "block_market": "48"
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 200:
        print(response.status_code, '请求失败！', f'请求参数：ind_code={ind_code}, date={date}')
        return pd.DataFrame()
    else:
        data = response.json()['data']['list']
        total = response.json()['data']['total']
        if total < 20:
            data = pd.DataFrame(data)
            data.rename(columns={'turnover': 'amount', 'stock_code': 'ticker', 'stock_name': 'name',
                                 'margin_of_increase': 'pct_change', 'net_inflow_of_main_force': 'nf_main',
                                 'turnover_rate': 'tovr'}, inplace=True)
            return data
        else:
            all_data = data.copy()
            for i in range(20, total, 20):
                payload = {
                    "block_code": f"{ind_code}",
                    "sort_info": {
                        "sort_field": "0",
                        "sort_type": "desc"
                    },
                    "history_info": {
                        "history_type": "1",
                        "end_date": f"{date}000000",
                        "start_date": f"{date}000000"
                    },
                    "page_info": {
                        "page_size": 20,
                        "page": i / 20 + 1
                    },
                    "block_market": "48"
                }
                response = requests.post(url, json=payload, headers=headers)
                if response.status_code != 200:
                    print(response.status_code, '循环中请求失败！', f'请求参数：ind_code={ind_code}, date={date}')
                    continue
                else:
                    data = response.json()['data']['list']
                    all_data += data
            data = pd.DataFrame(all_data)
            data.rename(columns={'turnover': 'amount', 'stock_code': 'ticker', 'stock_name': 'name',
                                 'margin_of_increase': 'pct_change', 'net_inflow_of_main_force': 'nf_main',
                                 'turnover_rate': 'tovr'}, inplace=True)
            return data


def fetch_ind_list(date, page):
    """
    获取单页数据。
    """
    url = 'https://dq.10jqka.com.cn/interval_calculation/block_info/v1/get_block_list'
    payload = {
        "sort_info": {
            "sort_field": "0",
            "sort_type": "desc"
        },
        "history_info": {
            "history_type": "0",
            "end_date": f"{date}150000",
            "start_date": f"{date}093000"
        },
        "type": 0,
        "page_info": {
            "page_size": 20,
            "page": page
        }
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 200:
        print(response.status_code, '请求失败！', f'请求参数：date={date}, page={page}')
        return []
    else:
        data = response.json()['data']
        return data


def get_ind_list(date):
    """
    获取指定日期的板块涨跌情况，20220822开始可以获取
    :param date: 指定日期，请传入字符串，例如20240322
    :return: pandas DataFrame
    """
    initial_data = fetch_ind_list(date, 1)
    if not initial_data:  # 如果初始请求失败，返回空DataFrame
        return pd.DataFrame()
    # noinspection PyTypeChecker
    total = initial_data['total']
    pages = total // 20 + (1 if total % 20 else 0)
    # noinspection PyTypeChecker
    all_data = initial_data['list'].copy()

    with ThreadPoolExecutor(max_workers=10) as executor:  # 可以调整max_workers来优化性能
        future_to_page = {executor.submit(fetch_ind_list, date, page): page for page in range(2, pages + 1)}
        for future in as_completed(future_to_page):
            page = future_to_page[future]
            try:
                data = future.result()['list']
                all_data += data
            except Exception as exc:
                print(f'页面 {page} 请求产生了异常: {exc}')

    data = pd.DataFrame(all_data)
    data.rename(columns={'turnover': 'amount', 'block_name': 'ind_name', 'margin_of_increase': 'pct_change',
                         'net_inflow_of_main_force': 'nf_main'}, inplace=True)
    data.drop(columns=['stock_list'], inplace=True)
    return data


def ind_index_data(ind_code):
    """
    获取一个板块的指数k线
    :param ind_code: 板块代码
    :return: pandas DataFrame
    """
    url = f'https://dq.10jqka.com.cn/interval_calculation/block_info/v1/get_latest_k_line?block_code={ind_code}&block_market=48'
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(response.status_code, '请求失败！')
    else:
        data = response.json()['data']['data_list']
        data = pd.DataFrame(data)
        data['date'] = data['date'].apply(lambda x: datetime.datetime.strptime(x, '%Y%m%d%H%M%S'))
        del data['yesterday_close_price']
        data.rename(columns={'high_price': 'high', 'low_price': 'low', 'open_price': 'open', 'close_price': 'close'}, inplace=True)
        return data

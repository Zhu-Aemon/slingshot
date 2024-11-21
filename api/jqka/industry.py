"""
Created on 2024.3.24
获取同花顺行业（传统行业、概念板块、地域板块）每天的涨跌和各成分股
"""
import requests
import datetime
import random
import json
import pandas as pd
import numpy as np

from concurrent.futures import ThreadPoolExecutor, as_completed
from get_pc_cookie import get_cookie_pc
from itertools import chain

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


def ind_k_recent(ind_code):
    """
    获取一个板块的指数k线，但是只能获取最近一些
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


def ind_k_all(ind_code):
    """
    获取一个板块所有的k线
    注意这里用的是同花顺网页版的API，这也就意味着cookie的设置必然和手机版的有所不同
    :param ind_code: 同花顺板块代码
    :return: DataFrame
    """
    # noinspection SpellCheckingInspection
    cookies_pc = {
        'historystock': ind_code,
        'spversion': '20130314',
        'v': get_cookie_pc(),
    }
    headers_pc = {
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'DNT': '1',
        'Referer': 'https://stockpage.10jqka.com.cn/',
        'Sec-Fetch-Dest': 'script',
        'Sec-Fetch-Mode': 'no-cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }
    response = requests.get(f'https://d.10jqka.com.cn/v6/line/bk_{ind_code}/01/all.js', cookies=cookies_pc, headers=headers_pc)
    data = response.text.lstrip(f'quotebridge_v6_line_bk_{ind_code}_01_all(').rstrip(')')
    data = json.loads(data)
    del data['afterVolumn']
    price = data['price'].split(',')
    price = [price[i * 4: (i + 1) * 4] for i in range(len(price) // 4)]
    price = np.array([[int(x[0]), int(x[0]) + int(x[1]), int(x[0]) + int(x[2]), int(x[0]) + int(x[3])] for x in price]) / data['priceFactor']  # 最低价，开盘价，最高价，收盘价
    volume = [int(x) for x in data['volumn'].split(',')]
    year = data['sortYear']
    year = [[str(x[0])] * x[1] for x in year]
    year = list(chain.from_iterable(year))
    dates = data['dates'].split(',')
    dates = [year[i] + dates[i] for i in range(len(dates))]
    data = pd.DataFrame(price, columns=['low', 'open', 'high', 'close'])
    data['date'] = dates
    data['date'] = data['date'].apply(lambda x: datetime.datetime.strptime(x, '%Y%m%d'))
    data['volume'] = volume
    data = data[['date', 'open', 'low', 'high', 'close', 'volume']]
    return data

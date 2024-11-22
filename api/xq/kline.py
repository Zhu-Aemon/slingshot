"""
获取雪球行情数据
Created on 2024.3.27
"""

import requests
import pandas as pd
import datetime
import time

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36",
    "Cookie": "xqat=691d6f0a678b98a172affb89759b9c46fd23b4e2; u=171732008163910"
}


# def get_new_cookie():
#     """
#     说明：雪球的xqat和u的值为请求的时候必须携带的参数，但是这个参数很容易过期，那这个时候我们可以在每次请求前都获取一个新的cookie
#     :return: None
#     """
#     res = requests.get('https://xueqiu.com/', headers=headers)
#     xqat = res.cookies.get('xqat')
#     u = res.cookies.get('u')
#     headers.update({'Cookie': f"xqat={xqat}; u={u}"})
#
#
# get_new_cookie()


def xq_intraday(symbol, period='5d'):
    """
    获取雪球分时数据，注意只可获取最近的一个或者五个交易日的！
    :param symbol: A股带交易所标识符，美股直接ticker
    :param period: 1d - 最近一天，5d - 最近五天
    :return: 当天的1min k线数据
    """
    url = 'https://stock.xueqiu.com/v5/stock/chart/minute.json'
    if len(symbol) == 6:
        if symbol.startswith('6'):
            symbol = 'SH' + symbol
        else:
            symbol = 'SZ' + symbol
    params = {
        "symbol": symbol,
        "period": period
    }
    response = requests.get(url, params=params, headers=headers)
    if response.status_code != 200:
        print(f'{response.status_code}，请求错误！')
        return pd.DataFrame()
    data = response.json()['data']['items']
    data = pd.DataFrame(data)
    data.rename(columns={'current': 'close', 'avg_price': 'avgp', 'timestamp': 'time'}, inplace=True)
    # data['time'] = data['time'].apply(datetime.datetime.utcfromtimestamp)
    if data.loc[1, 'capital']:
        data['caps'] = data['capital'].apply(lambda x: x['small'] if x else 0)
        data['capm'] = data['capital'].apply(lambda x: x['medium'] if x else 0)
        data['capl'] = data['capital'].apply(lambda x: x['large'] if x else 0)
        data['capxl'] = data['capital'].apply(lambda x: x['xlarge'] if x else 0)
    data.drop(columns=['macd', 'kdj', 'ratio', 'capital', 'volume_compare'], inplace=True)
    return data


def xq_trades(symbol, count=100):
    """
    获取成交明细，最多支持最近100条
    :param symbol: A股带交易所标识
    :param count: 返回条数，最多100，默认100
    :return: pandas DataFrame
    """
    url = 'https://stock.xueqiu.com/v5/stock/history/trade.json'
    if len(symbol) == 6:
        if symbol.startswith('6'):
            symbol = 'SH' + symbol
        else:
            symbol = 'SZ' + symbol
    params = {
        "symbol": symbol,
        "count": count
    }
    response = requests.get(url, params=params, headers=headers)
    if response.status_code != 200:
        print(f'{response.status_code}，请求失败！{response.text}')
        return pd.DataFrame()
    data = response.json()['data']['items']
    data = pd.DataFrame(data)
    data.rename(columns={'timestamp': 'time', 'side': 'bs'}, inplace=True)
    data = data[['time', 'current', 'chg', 'percent', 'trade_volume', 'bs']]
    return data


def xq_snapshot(symbol):
    """
    获取雪球实时盘口快照，请注意是实时的
    :param symbol: A股带交易所标识符
    :return: pandas DataFrame
    """
    url = 'https://stock.xueqiu.com/v5/stock/realtime/pankou.json'
    if len(symbol) == 6:
        if symbol.startswith('6'):
            symbol = 'SH' + symbol
        else:
            symbol = 'SZ' + symbol
    params = {
        "symbol": symbol,
    }
    response = requests.get(url, params=params, headers=headers)
    if response.status_code != 200:
        print(f'{response.status_code}，请求失败！{response.text}')
        return pd.DataFrame()
    data = response.json()['data']
    data = pd.DataFrame([data])
    data = data[['timestamp', 'bp1', 'bc1', 'bp2', 'bc2', 'bp3', 'bc3', 'bp4', 'bc4', 'bp5', 'bc5', 'sp1', 'sc1',
                 'sp2', 'sc2', 'sp3', 'sc3', 'sp4', 'sc4', 'sp5', 'sc5', 'buypct', 'sellpct', 'diff']]
    data.rename(columns={'timestamp': 'time', 'bc1': 'bv1', 'bc2': 'bv2', 'bc3': 'bv3', 'bc4': 'bv4', 'bc5': 'bv5',
                         'sc1': 'sv1', 'sc2': 'sv2', 'sc3': 'sv3', 'sc4': 'sv4', 'sc5': 'sv5'}, inplace=True)
    return data


def xq_kline(symbol, period='day', begin=int(time.time() * 1000), count=200):
    """
    获取雪球上的分钟级别k线数据
    :param symbol: A股带交易所标识符
    :param period: 1m - 分钟, 5m, 15m, 30m, 60m, 120m, year, quarter, month, day
    :param begin: 开始的时间戳，貌似是当前时间戳！
    :param count: k线根数
    :return: pandas DataFrame
    """
    if len(symbol) == 6:
        if symbol.startswith('6'):
            symbol = 'SH' + symbol
        else:
            symbol = 'SZ' + symbol
    url = f'https://stock.xueqiu.com/v5/stock/chart/kline.json'
    params = {
        "symbol": symbol,
        "begin": begin,
        "period": period,
        "type": "before",
        "count": -count,
        "indicator": "kline",
    }
    response = requests.get(url=url, params=params, headers=headers)
    if response.status_code != 200:
        print(response.status_code, '请求失败！', response.text)
        return pd.DataFrame()
    data = response.json()['data']
    data = pd.DataFrame(data['item'], columns=data['column'])
    data.rename(columns={'timestamp': 'time', 'turnoverrate': 'tovr'}, inplace=True)
    data.drop(columns=['volume_post', 'amount_post'], inplace=True)
    return data

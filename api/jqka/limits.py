import requests
import pandas as pd
import time
from datetime import datetime

# noinspection SpellCheckingInspection
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'DNT': '1',
    'Host': 'data.10jqka.com.cn',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Not(A:Brand";v="24", "Chromium";v="122"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"'
}


def daily_limits(date):
    """
    每天涨停股票的信息
    :param date: 日期字符串，例如20240322
    :return: pandas DataFrame
    """
    url = 'https://data.10jqka.com.cn/dataapi/limit_up/limit_up_pool'
    params = {
        "page": "1",
        "limit": "15",
        "field": "199112,10,9001,330323,330324,330325,9002,330329,133971,133970,1968584,3475914,9003,9004",
        "filter": "HS,GEM2STAR",
        "date": date,
        "order_field": "330324",
        "order_type": "0",
        "_": f'{int(time.time() * 1000)}'
    }
    response = requests.get(url, params=params, headers=headers)
    if response.status_code != 200:
        print(f'{response.text}，请求失败！')
        return pd.DataFrame()
    try:
        data = response.json()['data']
    except KeyError:
        return pd.DataFrame()
    count = data['page']['total']
    info = data['info']
    info = [{
        "open_num": x['open_num'],
        "tflim": x['first_limit_up_time'],
        'tllim': x['last_limit_up_time'],
        'code': x['code'],
        'type': x['limit_up_type'],
        'vlim': x['order_volume'],  # 封单量，多少手
        'lim_srate': x['limit_up_suc_rate'],
        'cirv': x['currency_value'],
        'rate': x['change_rate'],
        'tovr': x['turnover_rate'],
        'reason': x['reason_type'],
        'alim': x['order_amount'],  # 封单额，多少钱，单位元
        'height': x['high_days'],  # 第几个板
        'price': x['latest']
    } for x in info]
    res = [pd.DataFrame(info)]
    for num in range(15, count, 15):
        params = {
            "page": f'{int(num / 15 + 1)}',
            "limit": "15",
            "field": "199112,10,9001,330323,330324,330325,9002,330329,133971,133970,1968584,3475914,9003,9004",
            "filter": "HS,GEM2STAR",
            "date": date,
            "order_field": "330324",
            "order_type": "0",
            "_": f'{int(time.time() * 1000)}'
        }
        response = requests.get(url, params=params, headers=headers)
        if response.status_code != 200:
            print(f'{response.text}，循环中请求失败！')
            continue
        try:
            data = response.json()['data']
        except KeyError:
            continue
        count = data['page']['total']
        info = data['info']
        info = [{
            "open_num": x['open_num'],
            "tflim": x['first_limit_up_time'],
            'tllim': x['last_limit_up_time'],
            'code': x['code'],
            'type': x['limit_up_type'],
            'vlim': x['order_volume'],  # 封单量，多少手
            'lim_srate': x['limit_up_suc_rate'],
            'cirv': x['currency_value'],
            'rate': x['change_rate'],
            'tovr': x['turnover_rate'],
            'reason': x['reason_type'],
            'alim': x['order_amount'],  # 封单额，多少钱，单位元
            'height': x['high_days'],  # 第几个板
            'price': x['latest']
        } for x in info]
        res.append(pd.DataFrame(info))
    res = pd.concat(res)
    res.reset_index(inplace=True, drop=True)
    return res

"""
东方财富外汇数据
Created on 2023.3. 27
"""
import requests
import pandas as pd
import datetime
import time
import random

headers = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive',
    'Cookie': 'qgqp_b_id=032a4d9e059f44224c037bcea0cb584d; HAList=ty-0-159707-%u5730%u4EA7ETF; st_si=83867424369618; st_asi=delete; st_pvi=18511749580355; st_sp=2024-01-31%2009%3A38%3A35; st_inirUrl=https%3A%2F%2Fwap.eastmoney.com%2F; st_sn=21; st_psi=20240328002822526-113200301321-0786954420',
    'Host': 'push2.eastmoney.com',
    'Referer': 'https://quote.eastmoney.com/center/whsc.html',
    'Sec-Ch-Ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Sec-Fetch-Dest': 'script',
    'Sec-Fetch-Mode': 'no-cors',
    'Sec-Fetch-Site': 'same-site',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
}


def em_forex_live(symbol, history=True):
    """
    从东方财富获取实时的外汇数据，暂时不可以使用
    外汇和symbol对照表：
    美元离岸人民币 - 133.USDCHN
    美元指数 - 100.UDI
    欧元兑美元 - 119.EURUSD
    美元兑澳元 - 119.USDAUD
    美元兑港币 - 119.USDHKD
    英镑兑美元 - 119.GBPUSD
    美元兑日元 - 119.USDJPY
    :param symbol: 外汇对的symbol
    :param history: 是否返回完整的历史数据
    :return: pandas DataFrame
    """
    url = 'https://push2.eastmoney.com/api/qt/stock/trends2/get'
    cache_buster = f'cb_{int(time.time() * 1000)}_{random.randint(10000000, 99999999)}'
    params = {
        "secid": symbol,
        "fields1": "f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13",
        "fields2": "f51,f52,f53,f54,f55,f56,f57,f58",
        "ut": "e1e6871893c6386c5ff6967026016627",
        "iscr": "0",
        "isqhquote": "",
        "cb": cache_buster,
        f'{cache_buster}': cache_buster
    }
    response = requests.get(url, params=params, headers=headers)
    return response
    if response.status_code != 200:
        print(f'{response.status_code}，{response.text}，请求失败！')
        return pd.DataFrame()
    data = eval(response.text.lstrip(f'{cache_buster}(').rstrip(')'))['data']['trends']
    data = [x.split(',')[0] for x in data]
    data = pd.DataFrame(data, columns=['time', 'price'])
    if history:
        return data
    return data.loc[len(data) - 1, 'price']

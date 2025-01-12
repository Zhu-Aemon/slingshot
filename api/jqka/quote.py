from get_pc_cookie import get_cookie_pc

import requests
import orjson

import pandas as pd


def stock_quote(code: list):
    """
    获取实时的股票报价
    :param code: 股票六位代码的列表
    :return: pandas.DataFrame，price_ulim：涨停价，price_dlim：跌停价，committee：委比，commissioned - 委差
    """
    cookies = {
        'searchGuide': 'sg',
        'historystock': '301413',
        'spversion': '20130314',
        'v': get_cookie_pc(),
    }
    headers = {
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
    url = f'https://qd.10jqka.com.cn/quote.php?cate=real&type=stock&return=json&callback=showStockData&code={",".join(code)}'
    r = requests.get(url, cookies=cookies, headers=headers)
    data = pd.DataFrame(orjson.loads(r.text.lstrip('showStockData(').rstrip(')'))['data']).T
    data.rename(columns={'10': 'close', '8': 'high', '7': 'open', '9': 'low', '13': 'volume', '19': 'amount',
                         '15': 'SVol', '14': 'BVol', '69': 'price_ulim', '70': 'price_dlim', '1968584': 'turnover',
                         '2034120': 'PE(dynamic)', '526792': 'amplitude', '3475914': 'mktValTrd', '461256': 'committee',
                         '395720': 'commissioned', '6': 'lastClose'}, inplace=True)
    data = data[['open', 'high', 'low', 'close', 'volume', 'amount', 'SVol', 'BVol', 'price_ulim', 'price_dlim',
                 'turnover', 'PE(dynamic)', 'amplitude', 'mktValTrd', 'committee', 'commissioned', 'lastClose']]
    return data


def stock_lob(code: str):
    """
    获取五档盘口行情
    :param code: 六位股票代码
    :return: dict，bn - 买n，bvn - 买n的挂单量，sn - 卖n，svn - 卖n的挂弹量
    """
    cookies = {
        'searchGuide': 'sg',
        'historystock': '301413',
        'spversion': '20130314',
        'v': get_cookie_pc(),
    }
    headers = {
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
    url = f'https://d.10jqka.com.cn/v2/fiverange/hs_{code}/last.js'
    r = requests.get(url, cookies=cookies, headers=headers)
    data = orjson.loads(r.text.lstrip(f'quotebridge_v2_fiverange_hs_{code}_last(').rstrip(')'))['items']
    data = {
        'b1': data['24'],
        'bv1': data['25'],
        'b2': data['26'],
        'bv2': data['27'],
        'b3': data['28'],
        'bv3': data['29'],
        'b4': data['150'],
        'bv4': data['151'],
        'b5': data['154'],
        'bv5': data['155'],
        's1': data['30'],
        'sv1': data['31'],
        's2': data['32'],
        'sv2': data['33'],
        's3': data['34'],
        'sv3': data['35'],
        's4': data['152'],
        'sv4': data['153'],
        's5': data['156'],
        'sv5': data['157'],
    }
    return data


if __name__ == '__main__':
    print(stock_quote(['002085']))
    print(stock_lob('002085'))

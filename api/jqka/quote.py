from get_pc_cookie import get_cookie_pc

import requests
import orjson

import pandas as pd


def stock_quote(code: list):
    """
    获取实时的股票报价
    :param code: 股票六位代码的列表
    :return: pandas.DataFrame
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
    print(r.text)
    data = pd.DataFrame(orjson.loads(r.text.lstrip('showStockData(').rstrip(')'))['data']).T
    data.rename(columns={'10': 'close', '8': 'high', '7': 'open', '9': 'low', '13': 'volume', '19': 'amount',
                         '15': 'SVol', '14': 'BVol', '69': 'price_ulim', '70': 'price_dlim', '1968584': 'turnover',
                         '2034120': 'PE(dynamic)', '526792': 'amplitude', '3475914': 'mktValTrd', '461256': 'committee',
                         '395720': 'commissioned', '6': 'lastClose'}, inplace=True)
    data = data[['open', 'high', 'low', 'close', 'volume', 'amount', 'SVol', 'BVol', 'price_ulim', 'price_dlim',
                 'turnover', 'PE(dynamic)', 'amplitude', 'mktValTrd', 'committee', 'commissioned', 'lastClose']]
    return data


if __name__ == '__main__':
    import pymongo

    client = pymongo.MongoClient('mongodb://localhost:27017/')
    all_tickers = client['StockForum'].list_collection_names()[:1000]
    ticker_data = stock_quote(all_tickers)
    print(ticker_data)

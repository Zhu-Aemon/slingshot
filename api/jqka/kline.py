import requests
import orjson
import datetime

import numpy as np
import pandas as pd

from api.jqka.get_pc_cookie import get_cookie_pc
from itertools import chain


def stock_k_daily(code):
    """
    获取一个板块所有的k线
    注意这里用的是同花顺网页版的API，这也就意味着cookie的设置必然和手机版的有所不同
    :param code: 同花顺板块代码
    :return: DataFrame
    """
    # noinspection SpellCheckingInspection
    cookies_pc = {
        'historystock': code,
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
    response = requests.get(f'https://d.10jqka.com.cn/v6/line/hs_{code}/01/all.js', cookies=cookies_pc, headers=headers_pc)
    data = response.text.lstrip(f'quotebridge_v6_line_hs_{code}_01_all(').rstrip(')')
    data = orjson.loads(data)
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


if __name__ == '__main__':
    print(stock_k_daily('002085'))

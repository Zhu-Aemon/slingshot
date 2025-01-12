import pandas as pd

import requests
import time
import orjson
import random
import string
import datetime

from urllib.parse import quote


def generate_n_random(n):
    # Generate a n-digit random number
    random_number = random.randint(10**(n-1), 10**n - 1)
    return random_number


# noinspection SpellCheckingInspection
def market_quote():
    """
    获取最新的市场报价，全市场所有股票
    :return: pandas.DataFrame
    """
    cookies = {
        'qgqp_b_id': ''.join(random.choices(string.ascii_lowercase + string.digits, k=32)),
        'st_si': f'{generate_n_random(14)}',
        'st_asi': 'delete',
        'has_jump_to_web': '1',
        'st_pvi': f'{generate_n_random(14)}',
        'st_sp': quote(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        'st_inirUrl': 'https%3A%2F%2Fguba.eastmoney.com%2F',
        'st_sn': '1',
        'st_psi': f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}{generate_n_random(2)}-{generate_n_random(12)}-{generate_n_random(12)}",
        'fullscreengg': '1',
        'websitepoptg_api_time': f'{int(time.time() * 1000)}',
    }

    headers = {
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
        'DNT': '1',
        'Referer': 'https://quote.eastmoney.com/center/gridlist.html',
        'Sec-Fetch-Dest': 'script',
        'Sec-Fetch-Mode': 'no-cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    timestamp = int(time.time() * 1000)
    response = requests.get(
        f'https://72.push2.eastmoney.com/api/qt/clist/get?cb=jQuery112401712973253940706_{timestamp}&pn=1&pz=6000&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&dect=1&wbp2u=|0|0|0|web&fid=f3&fs=m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23,m:0+t:81+s:2048&fields=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152&_=1736657005081',
        cookies=cookies,
        headers=headers,
    )
    r = orjson.loads(response.text.lstrip(f'jQuery112401712973253940706_{timestamp}(').rstrip(');'))
    data = pd.DataFrame(r['data']['diff'])
    data.rename(columns={
        'f2': 'latest',
        'f3': 'pct_change',
        'f4': 'change',
        'f5': 'volume',
        'f6': 'amount',
        'f7': 'amplitude',
        'f8': 'turnover',
        'f9': 'PE(dynamic)',
        'f10': 'vol_ratio',
        'f12': 'ticker',
        'f14': 'name',
        'f15': 'high',
        'f16': 'low',
        'f17': 'open',
        'f18': 'lastClose',
        'f20': 'mktValTot',
        'f21': 'mktValTrd',
        'f23': 'PB',
    }, inplace=True)
    data = data[['ticker', 'name', 'open', 'high', 'low', 'latest', 'lastClose', 'volume', 'pct_change', 'change', 'amount', 'amplitude', 'turnover', 'PE(dynamic)', 'vol_ratio', 'mktValTot', 'mktValTrd', 'PB']]
    return data


if __name__ == '__main__':
    print(market_quote())

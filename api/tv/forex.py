import requests
import pandas as pd
from bs4 import BeautifulSoup
import json
import sqlite3


def tv_forex_group(area='asia'):
    """
    获取外汇实时数据
    :param area: 小写，空格-连接，支持：all, major, minor, exotic, americas, europe, asia, pacific, middle-east, africa
    """
    url = f'https://www.tradingview.com/markets/currencies/rates-{area}/'
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en,zh-CN;q=0.9,zh;q=0.8",
        "Cache-Control": "max-age=0",
        "Referer": "https://www.tradingview.com/markets/currencies/",
        "Sec-Ch-Ua": "\"Google Chrome\";v=\"123\", \"Not:A-Brand\";v=\"8\", \"Chromium\";v=\"123\"",
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": "\"Windows\"",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    }
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    raw_data = json.loads(soup.find_all('script', type="application/prs.init-data+json")[3].text)
    first_key = list(raw_data.keys())[0]
    records = [x['d'][2:11] for x in raw_data[first_key]['data']['screener']['data']['data']]
    return pd.DataFrame(records, columns=['pair', 'price', 'pct_change', 'change', 'bid', 'ask', 'high', 'low', 'rating'])


def cn_forex_crossrates():
    data = tv_forex_group()
    data = data[data['pair'].apply(lambda x: 'cny' in x.lower())]
    data.reset_index(inplace=True, drop=True)
    return data


def store_cn_data_live():
    data = cn_forex_crossrates()
    data.to_sql(con=sqlite3.connect('cn_fx_live.db'), if_exists='replace', name='live', index=False)


if __name__ == '__main__':
    store_cn_data_live()

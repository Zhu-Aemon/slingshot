import requests
import pandas as pd
from datetime import datetime

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'DNT': '1',
    'Host': 'eq.10jqka.com.cn',
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


def get_hot_intraday(date):
    """
    获取分时的热度信息，间隔5min
    :param date: 日期，字符串，例如20240322
    :return: pandas DataFrame
    """
    url = f"https://eq.10jqka.com.cn/open/api/hot_list/history/v1/rank?type=stock&date={date}"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f'{response.status_code}, 请求出错！')
        return pd.DataFrame()
    else:
        data = response.json()['data']['stock_list']
        records = [
            {
                "order": stock["order"],
                "code": stock["code"],
                "name": stock["name"],
                "time": datetime.strptime(stock["time"], '%Y%m%d%H%M'),
                "rate": float(stock["rate"]),
                "market": stock["market"],
                "block": stock["tag"]["concept_tag"][0],
                "ind_code": stock["tag"]["concept_tag"][1],
                "ind_name": stock["tag"]["concept_tag"][2]
            }
            for date, stocks in data.items()
            for stock in stocks
        ]
        return_data = pd.DataFrame(records)
        return_data.sort_values(by=['time', 'order'], inplace=True)
        return_data.reset_index(inplace=True, drop=True)
        return return_data

"""
获取中债国债指数
"""
import requests
import datetime
import pandas as pd
import numpy as np


def cb_cookie():
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en,zh-CN;q=0.9,zh;q=0.8',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
    }

    params = {
        'locale': 'zh_CN',
    }

    response = requests.get('https://yield.chinabond.com.cn/cbweb-mn/indices/single_index_query', params=params, headers=headers)
    return response.cookies['JSESSIONID']
    

def cb_index(index_id, type='CF', type_duration='总值'):
    """get china bond index data

    Args:
        index_id (_type_): specific index id
        type (str, optional): Defaults to 'CF'. CF - 财富, QJ - 全价，JJ - 净价
    """
    type_duration_dict = {
        "总值": "00",
        "1年以下": "01",
        "1-3年": "02",
        "3-5年": "03",
        "5-7年": "04",
        "7-10年": "05",
        "10年以上": "06",
        "0-3个月": "07",
        "3-6个月": "08",
        "6-9个月": "09",
        "9-12个月": "10",
        "0-6个月": "11",
        "6-12个月": "12",
        "自定义": "13",
        "0-2年": "14",
        "0-3年": "15",
        "0-5年": "16",
        "0-7年": "17",
        "0-10年": "18",
        "1-5年": "19",
        "1-7年": "20",
        "1-10年": "21",
        "5-10年": "22",
        "5年以上": "23"
    }
    type_duration = type_duration_dict[type_duration]
    JSESSIONID = cb_cookie()
    cookies = {
        'JSESSIONID': JSESSIONID,
        'ROUTEID': '.server1',
    }

    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Sec-Fetch-Site': 'same-origin',
        'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
        'Sec-Fetch-Mode': 'cors',
        'Origin': 'https://yield.chinabond.com.cn',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.4 Safari/605.1.15',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'empty',
        'X-Requested-With': 'XMLHttpRequest',
        'Priority': 'u=3, i',
    }

    response = requests.post(
        f'https://yield.chinabond.com.cn/cbweb-mn/indices/singleIndexQueryResult?indexid={index_id}&&qxlxt={type_duration}&&ltcslx=&&zslxt={type}ZS&&zslxt1=&&lx=1&&locale=zh_CN',
        cookies=cookies,
        headers=headers,
    )
    if 'emsg' in response.json().keys() and response.json()['emsg'] == '未查询到数据':
        print('没有符合要求的数据！')
        return pd.DataFrame()
    data = pd.DataFrame(response.json()[f'{type}ZS_{type_duration}'], index=['value']).T.reset_index()
    data.rename(columns={'index': 'date'}, inplace=True)
    data['date'] = data['date'].apply(lambda x: datetime.datetime.fromtimestamp(int(x) / 1000))
    data['value'] = data['value'].astype(np.float32)
    return data


if __name__ == "__main__":
    print(cb_index('2c9081e50e8767dc010e879387370009', type_duration='1-3年'))

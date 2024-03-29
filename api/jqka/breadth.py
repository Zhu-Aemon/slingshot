"""
获取市场宽度和上证指数相关的一些实时数据
Created on 2024.3.29
"""
import requests
import pandas as pd
import datetime

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Cookie': 'u_ukey=A10702B8689642C6BE607730E11E6E4A; u_uver=1.0.0; u_dpass=6%2BTqQGEKG%2BPv3BSM3kOI%2FjtILN2WvyxW%2FwlSPrUGZG0BszpJKKhuFQOU2Yd1kWol%2FsBAGfA5tlbuzYBqqcUNFA%3D%3D; u_did=D0741417FFF64A309544C3BE5696BBBC; u_ttype=WEB; v=A681XsHsFSfTmhEb2vOCx4DEOMi8VAN2nagHasE8S54lEMF2ySSTxq14l7vS',
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


def breadth_live():
    """
    调用这个函数以获得实时的市场宽度数据
    :return: python dict
    """
    url = 'https://dq.10jqka.com.cn/fuyao/up_down_distribution/distribution/v2/realtime'
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f'{response.status_code}, {response.text}', '请求失败！')
        return pd.DataFrame()
    data = response.json()['data']
    records = {
        'suspend': data['suspend'],
        'time': data['last_update_time'],
        'limit_down': data['limit_down'],
        'limit_up': data['limit_up'],
        'flat': data['flat'],
        'up': data['up'],
        'down': data['down'],
        '-10': [x['value'] for x in data['table'] if x['key'] == '>10%'][0],
        '-10-7': [x['value'] for x in data['table'] if x['key'] == '10~7'][0],
        '-7-5': [x['value'] for x in data['table'] if x['key'] == '7~5'][0],
        '-5-3': [x['value'] for x in data['table'] if x['key'] == '5~3'][0],
        '-3-0': [x['value'] for x in data['table'] if x['key'] == '3~0'][0],
        '0': [x['value'] for x in data['table'] if x['key'] == '0'][0],
        '0-3': [x['value'] for x in data['table'] if x['key'] == '0~3'][0],
        '3-5': [x['value'] for x in data['table'] if x['key'] == '3~5'][0],
        '5-7': [x['value'] for x in data['table'] if x['key'] == '5~7'][0],
        '7-10': [x['value'] for x in data['table'] if x['key'] == '7~10'][0],
        '10': [x['value'] for x in data['table'] if x['key'] == '>10%'][1],
    }
    return records


def breadth_intraday(date='20240329', level=11):
    """
    获取历史分时日内市场宽度信息
    :param date: 例如20240329
    :param level: 分多少层，默认11，可选23
    :return: pandas DataFrame
    """
    url = 'https://eq.10jqka.com.cn/open/api/quote_review/rise_fall/v1/chart'
    params = {
        "level": level,
        "date": date
    }
    response = requests.get(url, params=params, headers=headers)
    if response.status_code != 200:
        print(response.status_code, response.text, '请求失败！')
        return pd.DataFrame()
    data = response.json()['data']['point_list']
    columns = response.json()['data']['point_key_list']
    columns = [x['name'] for x in columns]
    result = pd.DataFrame(data=data, columns=columns)
    result['日期'] = result['日期'].apply(lambda x: datetime.datetime.strptime(x, '%Y%m%d%H%M'))
    return result

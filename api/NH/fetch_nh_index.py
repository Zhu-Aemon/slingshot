import requests
import datetime
import pandas as pd
import numpy as np


def fetch_nh_index(index_code):
    cookies = {
        'sajssdk_2015_cross_new_user': '1',
        'sensorsdata2015jssdkcross': '%7B%22distinct_id%22%3A%22197aaf6babf7dc-011b0a2f0e65d69-152f2d66-334836-197aaf6bac017b3%22%2C%22first_id%22%3A%22%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMTk3YWFmNmJhYmY3ZGMtMDExYjBhMmYwZTY1ZDY5LTE1MmYyZDY2LTMzNDgzNi0xOTdhYWY2YmFjMDE3YjMifQ%3D%3D%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%22%2C%22value%22%3A%22%22%7D%2C%22%24device_id%22%3A%22197aaf6babf7dc-011b0a2f0e65d69-152f2d66-334836-197aaf6bac017b3%22%7D',
    }

    headers = {
        'Sec-Fetch-Site': 'same-origin',
        'Connection': 'keep-alive',
        'Sec-Fetch-Mode': 'cors',
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 nanhuaappua/01 (channel=ios;version=7.76.0;env=prd;store=iOS)',
        'Referer': 'https://mall.nanhua.net/rsh/nhzc/',
        'Sec-Fetch-Dest': 'empty',
        'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
    }

    params = {
        'productIds': index_code,
    }

    response = requests.get(
        'https://mall.nanhua.net/research-api/analyst/indexTrend',
        params=params,
        cookies=cookies,
        headers=headers,
    )
    try:
        data = response.json()['data'][0]['datas']
        data = pd.DataFrame(data)  # tradingDay, value
        data['tradingDay'] = data['tradingDay'].apply(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d'))
        data['value'] = data['value'].astype(np.float32)
    except (KeyError, IndexError) as e:
        print(f'An error occured during parsing: {e.__class__.__name__}, {e}')
        return pd.DataFrame()
    return data


if __name__ == "__main__":
    print(fetch_nh_index('NHCI'))

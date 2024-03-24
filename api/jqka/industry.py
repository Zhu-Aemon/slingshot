"""
Created on 2024.3.24
获取同花顺行业（传统行业、概念板块、地域板块）每天的涨跌和各成分股
"""
import requests
import pandas as pd

headers = {
    "Host": "dq.10jqka.com.cn",
    "Accept": "application/json, text/plain, */*",
    "Sec-Fetch-Site": "cross-site",
    "Accept-Language": "zh-CN,zh-Hans;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Sec-Fetch-Mode": "cors",
    "Content-Type": "application/json",
    "Origin": "https://localhost:8088",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Safari/604.1 Falcon/0.3.29 userid/712680386",
    "Referer": "https://localhost:8088/",
    "Connection": "keep-alive"
}


def ind_stock_list(ind_code, date):
    """
    获取一个板块对应的股票列表和涨跌，指定日期
    :param ind_code: 板块代码，同花顺定义的
    :param date: 想获取哪一天的，请传入字符串，例如20240322
    :return: DataFrame，内容是各成分股和涨跌
    """
    url = "https://dq.10jqka.com.cn/interval_calculation/stock_info/v1/get_stock_list_by_block"
    payload = {
        "block_code": f"{ind_code}",
        "sort_info": {
            "sort_field": "0",
            "sort_type": "desc"
        },
        "history_info": {
            "history_type": "1",
            "end_date": f"{date}000000",
            "start_date": f"{date}000000"
        },
        "page_info": {
            "page_size": 20,
            "page": 1
        },
        "block_market": "48"
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 200:
        print(response.status_code, '请求失败！', f'请求参数：ind_code={ind_code}, date={date}')
        return pd.DataFrame()
    else:
        data = response.json()['data']['list']
        total = response.json()['data']['total']
        if total < 20:
            data = pd.DataFrame(data)
            return data
        else:
            all_data = data.copy()
            for i in range(20, total, 20):
                payload = {
                    "block_code": f"{ind_code}",
                    "sort_info": {
                        "sort_field": "0",
                        "sort_type": "desc"
                    },
                    "history_info": {
                        "history_type": "1",
                        "end_date": f"{date}000000",
                        "start_date": f"{date}000000"
                    },
                    "page_info": {
                        "page_size": 20,
                        "page": i / 20 + 1
                    },
                    "block_market": "48"
                }
                response = requests.post(url, json=payload, headers=headers)
                if response.status_code != 200:
                    print(response.status_code, '循环中请求失败！', f'请求参数：ind_code={ind_code}, date={date}')
                    continue
                else:
                    data = response.json()['data']['list']
                    all_data += data
            data = pd.DataFrame(all_data)
            return data


def get_ind_list(date):
    """
    获取指定日期的板块涨跌情况
    :param date: 指定日期，请传入字符串，例如20240322
    :return: python dict
    """
    url = 'https://dq.10jqka.com.cn/interval_calculation/block_info/v1/get_block_list'
    payload = {
        "sort_info": {
            "sort_field": "0",
            "sort_type": "desc"
        },
        "history_info": {
            "history_type": "0",
            "end_date": f"{date}150000",
            "start_date": f"{date}093000"
        },
        "type": 0,
        "page_info": {
            "page_size": 20,
            "page": 1
        }
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 200:
        print(response.status_code, '请求失败！', f'请求参数：date={date}')
        return pd.DataFrame()
    else:
        data = response.json()['data']['list']
        total = response.json()['data']['total']
        if total < 20:
            return data
        else:
            all_data = data.copy()
            for i in range(20, total, 20):
                payload = {
                    "sort_info": {
                        "sort_field": "0",
                        "sort_type": "desc"
                    },
                    "history_info": {
                        "history_type": "0",
                        "end_date": f"{date}150000",
                        "start_date": f"{date}093000"
                    },
                    "type": 0,
                    "page_info": {
                        "page_size": 20,
                        "page": i / 20 + 1
                    }
                }
                response = requests.post(url, json=payload, headers=headers)
                if response.status_code != 200:
                    print(response.status_code, '循环中请求失败！', f'请求参数：date={date}')
                    continue
                else:
                    data = response.json()['data']['list']
                    all_data += data
            return all_data

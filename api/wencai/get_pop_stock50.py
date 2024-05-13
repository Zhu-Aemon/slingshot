"""
获取问财上热门的股票，数据从2021年开始
"""
import requests
import pandas as pd


def get_pop50(date='20210101'):
    url = 'https://www.iwencai.com/customized/chart/get-robot-data'
    # noinspection SpellCheckingInspection
    data = {
        'add_info': '{"urp":{"scene":1,"company":1,"business":1},"contentType":"json","searchInfo":true}',
        'block_list': '',
        'log_info': '{"input_type":"click"}',
        'page': 1,
        'perpage': '50',
        'query_area': '',
        'question': f'热门50股票 日期{date}',
        'rsh': 'Ths_iwencai_Xuangu_30a4yizh6plqm3kfd0dpr3g9s8ak47px',
        'secondary_intent': 'stock',
        'source': 'Ths_iwencai_Xuangu',
        'version': '2.0'
    }
    # noinspection SpellCheckingInspection
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en,zh-CN;q=0.9,zh;q=0.8",
        "Cache-control": "no-cache",
        "Connection": "keep-alive",
        "Content-Length": "384",
        "Content-Type": "application/json",
        "Cookie": "cid=48469db01eb6c2c50f5c54670631d03d1715520329; other_uid=Ths_iwencai_Xuangu_30a4yizh6plqm3kfd0dpr3g9s8ak47px; ta_random_userid=cgbr36zzy7; v=Axd8gpqxPS8hbrmjzt6m9-OApoBkXOu9xTBvMmlEM-ZNmDn-cSx7DtUA_4V6",
        "Host": "www.iwencai.com",
        "Origin": "https://www.iwencai.com",
        "Pragma": "no-cache",
        "Referer": "https://www.iwencai.com/unifiedwap/home/index",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "hexin-v": "Axd8gpqxPS8hbrmjzt6m9-OApoBkXOu9xTBvMmlEM-ZNmDn-cSx7DtUA_4V6",
        "sec-ch-ua": "\"Chromium\";v=\"124\", \"Google Chrome\";v=\"124\", \"Not-A.Brand\";v=\"99\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\""
    }
    r = requests.post(url=url, headers=headers, json=data)
    if r.status_code != 200:
        print('请求错误！', r.text)
        return
    result = r.json()['data']['answer'][0]['txt'][0]['content']['components'][0]['data']['datas']
    result = pd.DataFrame(result)
    return result

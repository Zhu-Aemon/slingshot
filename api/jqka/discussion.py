"""
Created on 2024/3.25
获取同花顺讨论内容
"""
import requests
import pandas as pd
import datetime
import pytz

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'DNT': '1',
    'Host': 't.10jqka.com.cn',
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


def jqka_discussion_latest(page=1, page_size=15, pid=0, time=0, sort='publish', code='603721', market_id='17'):
    """
    获取同花顺论坛上的内容，按照时间排序
    https://t.10jqka.com.cn/lgt/post/open/api/forum/post/v2/recent?page=1&page_size=15&pid=0&time=0&sort=publish&code=603721&market_id=17
    :param page: 分页
    :param page_size: 固定15，别改
    :param pid: 别改
    :param time: 别改
    :param sort: public - 按照发布帖子的最新时间sort，reply - 按照最新回复sort
    :param code: 代码，不带交易所标识符
    :param market_id: 17，别改
    :return: pandas DataFrame
    """
    url = 'https://t.10jqka.com.cn/lgt/post/open/api/forum/post/v2/recent'
    params = {
        "page": page,
        "page_size": page_size,
        "pid": pid,
        "time": time,
        "sort": sort,
        "code": code,
        "market_id": market_id
    }
    response = requests.get(url, params=params, headers=headers)
    if response.status_code != 200:
        print(f'{response.status_code}，请求失败！')
    else:
        data = response.json()['data']['feed']
        records = [
            {
                "pid": post['pid'],
                "uid": post['uid'],
                "fid": post['fid'],
                "content": post['content'],
                "device": post['from_id'],
                "ptime": pytz.timezone('Asia/Shanghai').localize(datetime.datetime.utcfromtimestamp(post['ctime'])),
                "mtime": pytz.timezone('Asia/Shanghai').localize(datetime.datetime.utcfromtimestamp(post['mtime'])),
                "user_name": post['user']['nickname'],
                "user_v": post['user']['is_v'],
                "user_age": post['user']['stock_age'],
                "ip_location": post['ip_location']['province_id'] if 'ip_location' in post.keys() else '',
                "reply": post['stat']['reply'],
                "share": post['stat']['share'],
                "like": post['stat']['like'],
                "forward": post['stat']['forward'],
                "comments": [{
                    "cid": comment['cid'],
                    "content": comment['content'],
                    "uid": comment['from_user']['uid'],
                    "user_name": comment['from_user']['nickname'],
                    "user_v": comment['from_user']['is_v'],
                    "user_age": comment['from_user']['stock_age']
                } for comment in post.get('comments', [])]
            }
            for post in data
        ]
        return_data = pd.DataFrame(records)
        return return_data


def jqka_discussion_recommended(page=1, code='603721', refresh_type=1, market_id=17):
    """
    获取某一只股票的推荐讨论post
    :param page: 分页，改变似乎没有作用
    :param code: 股票代码，不包含交易所标识符
    :param refresh_type: 默认1，别改
    :param market_id: 17，别改
    :return: pandas DataFrame
    """
    url = 'https://t.10jqka.com.cn/lgt/post/open/api/v1/recommend/list'
    params = {
        "page": page,
        "code": code,
        "refresh_type": refresh_type,
        "market_id": market_id
    }
    response = requests.get(url, params=params, headers=headers)
    if response.status_code != 200:
        print(f'{response.status_code}，请求失败！')
        return pd.DataFrame()
    data = response.json()
    if data['status_code'] != 0:
        print(f'{data["status_code"]}，返回数据失败！{data}')
        return pd.DataFrame()
    data = data['data']['recommend']
    records = [
        {
            "pid": post['pid'],
            "uid": post['uid'],
            "fid": post['fid'],
            "content": post['content'],
            "device": post['from_id'],
            "ptime": pytz.timezone('Asia/Shanghai').localize(datetime.datetime.utcfromtimestamp(post['ctime'])),
            "mtime": pytz.timezone('Asia/Shanghai').localize(datetime.datetime.utcfromtimestamp(post['mtime'])),
            "user_name": post['user']['nickname'],
            "user_v": post['user']['is_v'],
            "user_age": post['user']['stock_age'],
            "ip_location": post['ip_location']['province_id'],
            "reply": post['stat']['reply'],
            "share": post['stat']['share'],
            "like": post['stat']['like'],
            "forward": post['stat']['forward'],
            "comments": [{
                "cid": comment['cid'],
                "content": comment['content'],
                "uid": comment['from_user']['uid'],
                "user_name": comment['from_user']['nickname'],
                "user_v": comment['from_user']['is_v'],
                "user_age": comment['from_user']['stock_age']
            } for comment in post.get('comments', [])]
        }
        for post in data
    ]
    return_data = pd.DataFrame(records)
    return return_data

"""
获取交易日期
Created by Tianzhu Wang on 20240401
"""
import requests


def trading_days(start_date: str = '20190101'):
    """
    获取交易日历
    :param start_date: 从哪一天开始算
    :return: list[str]
    """
    # noinspection HttpUrlsUsage
    url = f'http://dsfwt.10jqka.com.cn/bidding/api/tradingday/startdate/{start_date}'
    # noinspection SpellCheckingInspection,HttpUrlsUsage
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,zh-TW;q=0.8,en;q=0.7",
        "Connection": "close",
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        "Cookie": "sessionid=15358e32dfe6a519f28ededa1f21d8d22; jgbsessid=8c16101ce87ac72c4790f7b2bc159d1e; THSFT_USERID=zyzq3602; u_name=zyzq3602; userid=682593258; user=Onp5enEzNjAyOjo6Ojo1NCwxMTAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDA",
        "Referer": "http://vis-free.10jqka.com.cn/billboard/ifind/html/index.html?theme=newgrey"
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f'{response.text}，请求失败！')
        return []
    return response.json()['data']

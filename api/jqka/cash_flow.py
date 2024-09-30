"""
获取资金流向的相关数据

9.30 获取沪深港通相关数据
"""
import requests
import pandas as pd


def hshkconnect_net_buy(date="2024-09-23", direction="south", page_index=1, proxy='n') -> pd.DataFrame:
    """
    获取沪深港通净买入数据，截止2024年9月是有544只港股通标的，注意page_index
    :param date: 格式yy-mm-dd，例如2024-09-23
    :param direction: 南向资金 - south; 北向资金 - north
    :param page_index: 第几页
    :param proxy: 所使用的代理，如果不特定指定的话那就默认没有，只需要写例如10.10.1.10:3128就可以
    :return:
    """
    url = "https://apigate.10jqka.com.cn/d/hq/hshkconnect/stock/net_buy_list/get_list"
    params = {
        "type": direction,
        "query_type": "one",
        "start_date": date,
        "sort_field": "net_buy_amount",
        "sort_mode": "desc",
        "page_index": f"{page_index}",
        "page_size": "20"
    }

    # noinspection SpellCheckingInspection
    headers = {
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Accept-Encoding": "gzip, deflate, br",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 hxFont/normal getHXAPPAdaptOldSetting/0 Language/zh-Hans getHXAPPAccessibilityMode/0 hxnoimage/0 getHXAPPFontSetting/normal VASdkVersion/1.1.8 VoiceAssistantVer/0 hxtheme/0 IHexin/11.60.30 (Royal Flush) innerversion/I037.08.528 build/11.60.31 surveyVer/0 isVip/0",
        "Host": "apigate.10jqka.com.cn",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh-Hans;q=0.9",
        "Connection": "keep-alive",
        "Referer": "https://eq.10jqka.com.cn/",
        "Sec-Fetch-Site": "same-site",
        "Origin": "https://eq.10jqka.com.cn"
    }
    # Send the GET request
    if proxy == 'n':
        response = requests.get(url, headers=headers, params=params)
    else:
        proxies = {
            'http': 'http://' + proxy,
            'https': 'https://' + proxy
        }
        response = requests.get(url, headers=headers, params=params, proxies=proxies)

    if response.status_code == 200:
        data = response.json()['data']
        # total_pages = data['pages']
        data_list = data['list']
        final_data = [
            {
                '股票代码': x['thscode_hq'],
                '名称': x['stock_name'],
                '日期': date,
                '净买入额': x['net_buy_amount'],
                '总成交额': x['turnover_amount'],
                '涨幅(%)': x['rate'],
                '增仓比例': x['add_hold_percentage'],
                '持股成本': x['purchase_cost'],
                '盈亏比': x['profit_percentage'],
                '累计持股成本': x['average_purchase_cost'],
                '累计持股盈亏': x['total_profit'],
                '港股通持股量': x['hold_num'],
                '持股市值': x['calc_hold_market_value'],
                '占总股本比例': x['hold_calc_percentage'],
                '净买入天数': x['net_buy_day_num']
            }
            for x in data_list
        ]
        final_data = pd.DataFrame(final_data)
        return final_data
    else:
        print(response.text)
        return pd.DataFrame()

"""
获取问财上热门的股票，数据从2021年开始
"""
from json import JSONDecodeError
from typing import Optional

import requests
import pandas as pd


# noinspection SpellCheckingInspection
def stock_hot_wc_50(date="20230815", proxy=None):
    """
    问财-热门股票排名
    https://www.iwencai.com/unifiedwap/result?w=%E7%83%AD%E9%97%A85000%E8%82%A1%E7%A5%A8&querytype=stock&issugs&sign=1620126514335
    :param date: 查询日期
    :type date: str
    :param proxy: 代理
    :return: 热门股票排名
    :rtype: pandas.DataFrame
    """
    url = "https://www.iwencai.com/gateway/urp/v7/landing/getDataList"
    params = {
        "query": "热门50股票",
        "urp_sort_way": "desc",
        "urp_sort_index": f"个股热度[{date}]",
        "page": "1",
        "perpage": "50",
        "addheaderindexes": "",
        "condition": '[{"chunkedResult":"热门50股票","opName":"and","opProperty":"","uiText":"个股热度排名<=50且个股热度从大到小排名","sonSize":3,"queryText":"个股热度排名<=50且个股热度从大到小排名","relatedSize":3},{"reportType":"NATURAL_DAILY","dateType":"+区间","indexName":"个股热度排名","indexProperties":["nodate 1","交易日期 20230817","<=50"],"valueType":"_整型数值","domain":"abs_股票领域","sonSize":0,"relatedSize":0,"source":"new_parser","tag":"个股热度排名","type":"index","indexPropertiesMap":{"<=":"50","交易日期":"20230817","nodate":"1"}},{"opName":"sort","opProperty":"从大到小排名","sonSize":1,"relatedSize":0},{"reportType":"NATURAL_DAILY","dateType":"+区间","indexName":"个股热度","indexProperties":["nodate 1","起始交易日期 20230817","截止交易日期 20230817"],"valueType":"_浮点型数值","domain":"abs_股票领域","sonSize":0,"relatedSize":0,"source":"new_parser","tag":"个股热度","type":"index","indexPropertiesMap":{"起始交易日期":"20230817","截止交易日期":"20230817","nodate":"1"}}]'.replace(
            "20230817", date
        ),
        "codelist": "",
        "indexnamelimit": "",
        "ret": "json_all",
        "source": "Ths_iwencai_Xuangu",
        "date_range[0]": date,
        "date_range[1]": date,
        "urp_use_sort": "1",
        "uuids[0]": "24087",
        "query_type": "stock",
        "comp_id": "6836372",
        "business_cat": "soniu",
        "uuid": "24087",
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
    }
    try:
        r = requests.get(url, params=params, headers=headers, proxies={'https': f'https://{proxy}'}, timeout=5)
    except (requests.Timeout, requests.exceptions.ProxyError, requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout):
        return 'time out'
    if 'Nginx forbidden' in r.text:
        return 'IP proxy error!'
    try:
        data_json = r.json()
        data = pd.DataFrame(data_json["answer"]["components"][0]["data"]["datas"])
    except JSONDecodeError:
        return 'IP proxy error!'
    return data


def stock_hot_wc_5000(date: str = "20230815", proxy: Optional[str] = None):
    """
    问财-热门股票排名
    https://www.iwencai.com/unifiedwap/result?w=%E7%83%AD%E9%97%A85000%E8%82%A1%E7%A5%A8&querytype=stock&issugs&sign=1620126514335
    :param date: 查询日期
    :param proxy: 代理
    :type date: str
    :return: 热门股票排名
    :rtype: pandas.DataFrame
    """
    url = "https://www.iwencai.com/gateway/urp/v7/landing/getDataList"
    # noinspection SpellCheckingInspection
    params = {
        "query": "热门5000股票",
        "urp_sort_way": "desc",
        "urp_sort_index": f"个股热度[{date}]",
        "page": "1",
        "perpage": "100",
        "addheaderindexes": "",
        "condition": '[{"chunkedResult":"热门5000股票","opName":"and","opProperty":"","uiText":"个股热度排名<=5000且个股热度从大到小排名","sonSize":3,"queryText":"个股热度排名<=5000且个股热度从大到小排名","relatedSize":3},{"reportType":"NATURAL_DAILY","dateType":"+区间","indexName":"个股热度排名","indexProperties":["nodate 1","交易日期 20230817","<=5000"],"valueType":"_整型数值","domain":"abs_股票领域","sonSize":0,"relatedSize":0,"source":"new_parser","tag":"个股热度排名","type":"index","indexPropertiesMap":{"<=":"5000","交易日期":"20230817","nodate":"1"}},{"opName":"sort","opProperty":"从大到小排名","sonSize":1,"relatedSize":0},{"reportType":"NATURAL_DAILY","dateType":"+区间","indexName":"个股热度","indexProperties":["nodate 1","起始交易日期 20230817","截止交易日期 20230817"],"valueType":"_浮点型数值","domain":"abs_股票领域","sonSize":0,"relatedSize":0,"source":"new_parser","tag":"个股热度","type":"index","indexPropertiesMap":{"起始交易日期":"20230817","截止交易日期":"20230817","nodate":"1"}}]'.replace(
            "20230817", date
        ),
        "codelist": "",
        "indexnamelimit": "",
        "ret": "json_all",
        "source": "Ths_iwencai_Xuangu",
        "date_range[0]": date,
        "date_range[1]": date,
        "urp_use_sort": "1",
        "uuids[0]": "24087",
        "query_type": "stock",
        "comp_id": "6836372",
        "business_cat": "soniu",
        "uuid": "24087",
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
    }
    big_df = pd.DataFrame()
    for page in range(1, 51):
        params.update(
            {
                "page": page,
            }
        )
        try:
            r = requests.get(url, params=params, headers=headers, proxies={'https': f'https://{proxy}'}, timeout=5)
        except (requests.Timeout, requests.exceptions.ProxyError, requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout):
            return 'time out!'
        if 'Nginx forbidden' in r.text:
            return 'IP proxy error!'
        try:
            data_json = r.json()
            temp_df = pd.DataFrame(data_json["answer"]["components"][0]["data"]["datas"])
        except JSONDecodeError:
            return 'IP proxy error!'
        big_df = pd.concat([big_df, temp_df], ignore_index=True)

    big_df.reset_index(inplace=True)
    big_df["index"] = range(1, len(big_df) + 1)
    try:
        rank_date_str = big_df.columns[1].split("[")[1].strip("]")
    except:
        try:
            rank_date_str = big_df.columns[2].split("[")[1].strip("]")
        except:
            rank_date_str = date
    big_df.rename(
        columns={
            "index": "rank",
            f"个股热度排名[{rank_date_str}]": "hot_rank",
            f"个股热度[{rank_date_str}]": "hotness",
            "code": "ticker",
            "market_code": "_",
            "最新涨跌幅": "change",
            "最新价": "latest",
            "股票代码": "_",
            "股票简称": "name"
        },
        inplace=True,
    )
    big_df = big_df[
        [
            "rank",
            "ticker",
            "name",
            "latest",
            "change",
            "hotness",
            "hot_rank",
        ]
    ]
    big_df["change"] = big_df["change"].astype(float).round(2)
    big_df["date"] = rank_date_str
    big_df["latest"] = pd.to_numeric(big_df["latest"], errors="coerce")
    return big_df

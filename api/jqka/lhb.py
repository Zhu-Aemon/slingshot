import requests
import pandas as pd
import time
import json


# noinspection SpellCheckingInspection
def get_lhb_data(date):
    """
    获取指定日期的龙虎榜数据
    date格式：2024-04-01
    """
    timestamp = int(time.time() * 1000)
    url = f'https://datacenter-web.eastmoney.com/api/data/v1/get?callback=jQuery112303442180237847381_{timestamp}&sortColumns=SECURITY_CODE%2CTRADE_DATE&sortTypes=1%2C-1&pageSize=500&pageNumber=1&reportName=RPT_DAILYBILLBOARD_DETAILSNEW&columns=SECURITY_CODE%2CSECUCODE%2CSECURITY_NAME_ABBR%2CTRADE_DATE%2CEXPLAIN%2CCLOSE_PRICE%2CCHANGE_RATE%2CBILLBOARD_NET_AMT%2CBILLBOARD_BUY_AMT%2CBILLBOARD_SELL_AMT%2CBILLBOARD_DEAL_AMT%2CACCUM_AMOUNT%2CDEAL_NET_RATIO%2CDEAL_AMOUNT_RATIO%2CTURNOVERRATE%2CFREE_MARKET_CAP%2CEXPLANATION%2CD1_CLOSE_ADJCHRATE%2CD2_CLOSE_ADJCHRATE%2CD5_CLOSE_ADJCHRATE%2CD10_CLOSE_ADJCHRATE%2CSECURITY_TYPE_CODE&source=WEB&client=WEB&filter=(TRADE_DATE%3C%3D%27{date}%27)(TRADE_DATE%3E%3D%27{date}%27)'
    r = requests.get(url=url)
    if r.status_code == 200 and r.text.startswith('jQuery'):
        data = r.text.rstrip(');').lstrip(f'jQuery112303442180237847381_{timestamp}(')
        data = json.loads(data)
        if data['result']['count'] > 500 or data['result']['pages'] > 1:
            print(f"{data['result']['count']}，一次请求不够！")
        return pd.DataFrame(data['result']['data'])
    return {}

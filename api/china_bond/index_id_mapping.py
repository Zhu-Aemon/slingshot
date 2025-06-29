import requests
import pandas as pd

cookies = {
    'JSESSIONID': '970A16C50064229BCBDEB2CA419E953C',
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

params = {
    'locale': 'zh_CN',
}

response = requests.post(
    'https://yield.chinabond.com.cn/cbweb-mn/indices/queryTree',
    params=params,
    cookies=cookies,
    headers=headers,
)

data = pd.DataFrame(response.json())
data.to_csv('china_bond_mapping.csv', index=False, encoding=False)

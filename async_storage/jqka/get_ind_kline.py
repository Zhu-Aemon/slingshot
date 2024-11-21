"""
Created on 2024.11.11
通过异步的方式获取同花顺上行业的K线并且存储到DolphinDB中
"""
import datetime
import random
import aiohttp
import time
import asyncio
import sys
import json

import pandas as pd
import dolphindb as ddb

from settings import *
from api.em.calendar import trading_days
from tqdm import tqdm
from json import JSONDecodeError
from collections import deque

concurrency = 10
proxy_get_count = 0
proxy_buffer = []
proxy_pool = deque(maxlen=concurrency)
proxy = None

headers = {
    "Host": "dq.10jqka.com.cn",
    "Accept": "application/json, text/plain, */*",
    "Sec-Fetch-Site": "cross-site",
    "Accept-Language": "zh-CN,zh-Hans;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Sec-Fetch-Mode": "cors",
    "Content-Type": "application/json",
    "Origin": "https://localhost:8088",
    "User-Agent": f"Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Safari/604.1 Falcon/0.3.29 userid/{random.randint(710000000, 712680385)}",
    "Referer": "https://localhost:8088/",
    "Connection": "keep-alive"
}

ddb_session = ddb.session(ddb_host, ddb_port, ddb_user, ddb_password)


async def get_proxy(lock) -> str:
    """
    获取代理池中的代理
    """
    global proxy_get_count, proxy_buffer
    async with lock:
        if len(proxy_buffer) > 0:
            proxy_get_count += 1
            return proxy_buffer.pop()
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://share.proxy.qg.net/get?key={proxy_key}' + r'&num=10&area=&isp=0&format=txt&seq=\r\n&distinct=true') as response:
                try:
                    r = await response.text()
                    r = json.loads(r)
                    print(r)
                except (JSONDecodeError, aiohttp.client_exceptions.ContentTypeError, KeyError):
                    r = await response.text()
                    proxies = r.split('\r\n')
                    proxy_buffer += proxies
        proxy_get_count += 1
        return proxy_buffer.pop()


async def initialize_proxy_pool(lock) -> None:
    """
    初始化代理池，一共50个代理
    """
    global proxy_pool, proxy_get_count, concurrency
    async with lock:
        proxy_get_count += concurrency
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://share.proxy.qg.net/get?key={proxy_key}&num={concurrency}' + r'&area=&isp=0&format=txt&seq=\r\n&distinct=true') as response:
            try:
                r = await response.text()
                r = json.loads(r)
                # print(r)
            except (JSONDecodeError, aiohttp.client_exceptions.ContentTypeError, KeyError):
                r = await response.text()
                proxies = r.split('\r\n')
                async with lock:
                    proxy_pool.extend(proxies)
                    print(proxy_pool)
                    print('代理池初始化成功！')


async def fetch_ind_list(date, page, session, proxy, lock):
    """
    获取单页数据。
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
            "page": page
        }
    }
    try:
        async with session.post(url, data=json.dumps(payload), headers=headers, ssl=False, proxy=f'http://{proxy}', timeout=10) as response:
            text = await response.text()
            data = json.loads(text)['data']
            return data, proxy
    except (asyncio.TimeoutError, aiohttp.ClientConnectionError, aiohttp.client_exceptions.ClientProxyConnectionError,
            aiohttp.client_exceptions.ClientHttpProxyError, aiohttp.http_exceptions.TransferEncodingError, aiohttp.client_exceptions.ClientPayloadError):
        proxy = get_proxy(lock)
        return await fetch_ind_list(date, page, session, proxy, lock)


async def get_ind_list_all(date, session, proxy, lock):
    """
    获取指定日期的板块涨跌情况，20220822开始可以获取
    :param date: 指定日期，请传入字符串，例如20240322，请确保输入的日期一定是一个交易日，否则可能会造成程序卡死！
    :param session: aiohttp.Session
    :param proxy: 格式如xx.xx.xx.xx:xx，字符串
    :param lock: asyncio.Lock
    :return: pandas DataFrame
    """
    initial_data, proxy = await fetch_ind_list(date, 1, session, proxy, lock)
    if not initial_data:  # 如果初始请求失败，返回空DataFrame
        return pd.DataFrame()
    # noinspection PyTypeChecker
    total = initial_data['total']
    pages = total // 20 + (1 if total % 20 else 0)
    all_data = initial_data['list'].copy()
    for p in tqdm(range(2, pages + 1)):
        data_iter, proxy = await fetch_ind_list(date, p, session, proxy, lock)
        all_data += data_iter['list']

    data = pd.DataFrame(all_data)
    data.rename(columns={'turnover': 'amount', 'block_name': 'ind_name', 'margin_of_increase': 'pct_change',
                         'net_inflow_of_main_force': 'nf_main'}, inplace=True)
    data.drop(columns=['stock_list'], inplace=True)
    return data, proxy


async def ind_index_data(ind_code, session, proxy, lock):
    """
    获取一个板块的指数k线
    :param ind_code: 板块代码
    :param session: aiohttp.Session
    :param proxy: 格式如xx.xx.xx.xx:xx，字符串
    :param lock: asyncio.Lock
    :return: pandas DataFrame
    """
    url = f'https://dq.10jqka.com.cn/interval_calculation/block_info/v1/get_latest_k_line?block_code={ind_code}&block_market=48'
    try:
        async with session.get(url, headers=headers, proxy=f'http://{proxy}', timeout=10, ssl=False) as response:
            text = await response.text()
            data = json.loads(text)['data']['data_list']
    except (asyncio.TimeoutError, aiohttp.ClientConnectionError, aiohttp.client_exceptions.ClientProxyConnectionError,
            aiohttp.client_exceptions.ClientHttpProxyError, aiohttp.http_exceptions.TransferEncodingError,
            aiohttp.client_exceptions.ClientPayloadError):
        proxy = get_proxy(lock)
        return await ind_index_data(ind_code, session, proxy, lock)
    data = pd.DataFrame(data)
    data['date'] = data['date'].apply(lambda x: datetime.datetime.strptime(x, '%Y%m%d%H%M%S'))
    del data['yesterday_close_price']
    data.rename(columns={'high_price': 'high', 'low_price': 'low', 'open_price': 'open', 'close_price': 'close', 'date': 'time'}, inplace=True)
    ddb_session.run(f"""
        db_path = "dfs://IndKline"
        if (not existsDatabase(db_path)) {{
            db = database(directory=db_path, partitionType=VALUE, partitionScheme=2000.01M + (0..30)*12, engine='OLAP')
        }} else {{
            db = database(db_path)
        }}

        if (not existsTable(db_path, 'I{ind_code}')) {{
            stkList = db.createTable(
                table(1000:0, `time`open`high`low`close, [DATE, DOUBLE, DOUBLE, DOUBLE, DOUBLE]),
                `I{ind_code}
            )
        }}
    """)
    ddb_session.upload({'tmp_table': data})
    ddb_session.run("""
        tableInsert(stkList, tmp_table)
    """)
    return proxy


async def get_ind_kline_with_semaphore(ind_code, session, lock, semaphore):
    global proxy_pool
    async with semaphore:
        async with lock:
            proxy = proxy_pool.popleft()
        proxy = await ind_index_data(ind_code, session, proxy, lock)
        async with lock:
            proxy_pool.append(proxy)


async def main():
    global start_time, proxy_pool, proxy_get_count
    trd_dates = trading_days('20150101')
    lock = asyncio.Lock()
    await initialize_proxy_pool(lock)
    semaphore = asyncio.Semaphore(concurrency)
    async with lock:
        ind_list_proxy = proxy_pool.popleft()
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False), trust_env=True) as session:
        ind_list, ind_list_proxy = await get_ind_list_all(trd_dates[-2], session, ind_list_proxy, lock)
        async with lock:
            proxy_pool.append(ind_list_proxy)
        ind_codes = ind_list['block_code']
        tasks = [get_ind_kline_with_semaphore(ind_code, session, lock, semaphore) for ind_code in ind_codes]
        for i, task in enumerate(asyncio.as_completed(tasks)):
            await task
            now_time = time.time()
            sys.stdout.write(
                f"\r耗时{now_time - start_time:.1f}s，正在爬取板块k线，进度：{(i + 1) / len(ind_codes) * 100:.2f}%，已经使用的代理数量：{proxy_get_count}")
            sys.stdout.flush()


if __name__ == '__main__':
    start_time = time.time()
    policy = asyncio.WindowsSelectorEventLoopPolicy()
    asyncio.set_event_loop_policy(policy)
    loop = asyncio.ProactorEventLoop()
    asyncio.set_event_loop(loop)
    asyncio.run(main())

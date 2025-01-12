"""
Created on 2025.1.12
通过异步的方式获取同花顺上股票的K线并且存储到DolphinDB中
"""
import datetime
import random

import aiohttp
import time
import asyncio
import sys
import json
import re

import pandas as pd
import numpy as np
import dolphindb as ddb

from settings import *
from api.jqka.get_pc_cookie import get_cookie_pc
from api.em.quote import market_quote
from collections import deque
from itertools import chain

concurrency = 15
proxy_get_count = 0
proxy_buffer = []
proxy_pool = deque(maxlen=concurrency)
proxy = None
last_req_time = 0

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
    global proxy_get_count, proxy_buffer, last_req_time
    async with lock:
        if len(proxy_buffer) > 0:
            proxy_get_count += 1
            return proxy_buffer.pop()
        url = re.sub(proxy_number_param + r'=\d{1,3}', f'{proxy_number_param}=10', proxy_url)
        if time.time() - last_req_time < 1:
            await asyncio.sleep(1 - time.time() + last_req_time)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                r = await response.text()
                last_req_time = time.time()
                proxies = r.split('\r\n')
                proxy_buffer += proxies
        proxy_get_count += 1
        return proxy_buffer.pop()


async def initialize_proxy_pool(lock) -> None:
    """
    初始化代理池，一共50个代理
    """
    global proxy_pool, proxy_get_count, concurrency, last_req_time
    async with lock:
        proxy_get_count += concurrency
    if time.time() - last_req_time < 1:
        await asyncio.sleep(1 - time.time() + last_req_time)
    url = re.sub(proxy_number_param + r'=\d{1,3}', f'{proxy_number_param}={concurrency}', proxy_url)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            r = await response.text()
            last_req_time = time.time()
            proxies = r.split('\r\n')
            async with lock:
                proxy_pool.extend(proxies)
                print(proxy_pool)
                print('代理池初始化成功！')


def convert_int(x):
    try:
        return int(x)
    except ValueError:
        return 0


# noinspection SqlResolve,SqlNoDataSourceInspection
async def get_stock_data(code, session, proxy, lock):
    """
    获取一只股票的k线，默认后复权
    :param code: 代码
    :param session: aiohttp.Session
    :param proxy: 格式如xx.xx.xx.xx:xx，字符串
    :param lock: asyncio.Lock
    :return: pandas DataFrame
    """
    cookies_pc = {
        'historystock': code,
        'spversion': '20130314',
        'v': get_cookie_pc(),
    }
    headers_pc = {
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'DNT': '1',
        'Referer': 'https://stockpage.10jqka.com.cn/',
        'Sec-Fetch-Dest': 'script',
        'Sec-Fetch-Mode': 'no-cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }
    url = f'https://d.10jqka.com.cn/v6/line/hs_{code}/02/all.js'
    try:
        async with session.get(url, headers=headers_pc, proxy=f'http://{proxy}', timeout=10, ssl=False, cookies=cookies_pc) as response:
            data = await response.text()
            if data == '':
                return proxy
            data = json.loads(data.lstrip(f'quotebridge_v6_line_hs_{code}_02_all(').rstrip(')'))
            del data['afterVolumn']
    except (asyncio.TimeoutError, aiohttp.ClientConnectionError, aiohttp.client_exceptions.ClientProxyConnectionError,
            aiohttp.client_exceptions.ClientHttpProxyError, aiohttp.http_exceptions.TransferEncodingError,
            aiohttp.client_exceptions.ClientPayloadError):
        proxy = await get_proxy(lock)
        return await get_stock_data(code, session, proxy, lock)

    price = data['price'].split(',')
    price = [price[i * 4: (i + 1) * 4] for i in range(len(price) // 4)]
    price = np.array([[convert_int(x[0]), convert_int(x[0]) + convert_int(x[1]), convert_int(x[0]) + convert_int(x[2]),
                       convert_int(x[0]) + convert_int(x[3])] for x in price]) / data['priceFactor']  # 最低价，开盘价，最高价，收盘价
    volume = [convert_int(x) for x in data['volumn'].split(',')]
    year = data['sortYear']
    year = [[str(x[0])] * x[1] for x in year]
    year = list(chain.from_iterable(year))
    dates = data['dates'].split(',')
    try:
        dates = [year[i] + dates[i] for i in range(len(dates))]
    except IndexError:
        return proxy
    data = pd.DataFrame(price, columns=['low', 'open', 'high', 'close'])
    data['time'] = dates
    data['time'] = data['time'].apply(lambda x: datetime.datetime.strptime(x, '%Y%m%d'))
    data['volume'] = volume
    data['ind_code'] = code
    data = data[['time', 'ind_code', 'open', 'low', 'high', 'close', 'volume']]

    ddb_session.run(f"""
        db_path = "dfs://stock"
        if (not existsDatabase(db_path)) {{
            db = database(directory=db_path, partitionType=VALUE, partitionScheme=2000.01M + (0..30)*12, engine='OLAP')
        }} else {{
            db = database(db_path)
        }}

        if (not existsTable(db_path, 'jqkaStkK')) {{
            stkList = createPartitionedTable(dbHandle=db,
                table=table(1000:0, `time`ticker`open`high`low`close`volume, [DATE, SYMBOL, DOUBLE, DOUBLE, DOUBLE, DOUBLE, LONG]),
                tableName=`jqkaStkK, partitionColumns=`time
            )
        }} else {{
            stkList = loadTable(db_path, 'jqkaStkK')
        }}
    """)
    ddb_session.upload({'tmp_table': data})
    ddb_session.run("""
        tableInsert(stkList, tmp_table)
    """)
    return proxy


async def get_stk_kline_with_semaphore(ind_code, session, lock, semaphore):
    global proxy_pool
    async with semaphore:
        async with lock:
            proxy = proxy_pool.popleft()
        proxy = await get_stock_data(ind_code, session, proxy, lock)
        async with lock:
            proxy_pool.append(proxy)


async def main():
    global start_time, proxy_pool, proxy_get_count
    lock = asyncio.Lock()
    await initialize_proxy_pool(lock)
    semaphore = asyncio.Semaphore(concurrency - 2)
    mkt_quote = market_quote()
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False), trust_env=True) as session:
        codes = list(mkt_quote['ticker'])
        existing_codes = list(ddb_session.run("""t = loadTable('dfs://stock', `jqkaStkK) \n select distinct(ticker) from t""")['distinct_ticker'])
        codes = list(set(codes) - set(existing_codes))
        print(codes)
        tasks = [get_stk_kline_with_semaphore(t, session, lock, semaphore) for t in codes]
        for i, task in enumerate(asyncio.as_completed(tasks)):
            await task
            now_time = time.time()
            sys.stdout.write(
                f"\r耗时{now_time - start_time:.1f}s，正在爬取股票k线，进度：{(i + 1) / len(codes) * 100:.2f}%，已经使用的代理数量：{proxy_get_count}")
            sys.stdout.flush()


if __name__ == '__main__':
    start_time = time.time()
    policy = asyncio.WindowsSelectorEventLoopPolicy()
    asyncio.set_event_loop_policy(policy)
    loop = asyncio.ProactorEventLoop()
    asyncio.set_event_loop(loop)
    asyncio.run(main())

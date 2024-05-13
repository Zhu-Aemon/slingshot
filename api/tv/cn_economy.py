import websocket
import json
import re
import pandas as pd
import sqlite3
from collections import defaultdict
import datetime


def get_cn_econ_data():
    sym_list = ['ECONOMICS:CNGDPYY', 'ECONOMICS:CNINTR', 'ECONOMICS:CNIRYY', 'ECONOMICS:CNUR', 'ECONOMICS:CNBOT',
                'ECONOMICS:CNGDG']

    messages = [[
        '~m~36~m~{"m":"set_data_quality","p":["low"]}',
        '~m~54~m~{"m":"set_auth_token","p":["unauthorized_user_token"]}',
        '~m~34~m~{"m":"set_locale","p":["en","US"]}',
        '~m~73~m~{"m":"chart_create_session","p":["cs_T9dn45uYEo2S","disable_statistics"]}',
        '~m~57~m~{"m":"switch_timezone","p":["cs_T9dn45uYEo2S","Etc/UTC"]}',
        '~m~78~m~{"m":"resolve_symbol","p":["cs_T9dn45uYEo2S","sds_sym_1","' + sym + '"]}',
        '~m~86~m~{"m":"create_series","p":["cs_T9dn45uYEo2S","sds_1","s1","sds_sym_1","1M",300,"120M"]}',
        '~m~82~m~{"m":"modify_series","p":["cs_T9dn45uYEo2S","sds_1","s1","sds_sym_1","1M","120M"]}',
    ] for sym in sym_list]
    print(messages)

    def on_message(ws, message):
        print(message)

    def on_open(ws, messages):
        print("Connection opened")
        # 发送消息
        # noinspection SpellCheckingInspection
        for msg in messages:
            ws.send(msg)
            print('send: ', msg)

    websocket.enableTrace(False)
    today = datetime.datetime.now()
    ws_instance = websocket.WebSocketApp(
        f"wss://data.tradingview.com/socket.io/websocket?from=markets%2Fworld-economy%2Fcountries%2Fchina%2F&date={today.strftime('%Y_%m_%d')}-11_22",
        on_message=on_message, on_open=on_open)
    ws_instance.run_forever()


if __name__ == "__main__":
    get_cn_econ_data()

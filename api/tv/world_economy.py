import websocket
import json
import re
import pandas as pd
import sqlite3
from collections import defaultdict
import datetime


# noinspection SpellCheckingInspection
def get_econ_data(countries: list[str] = ['US', 'CN', 'EU', 'JP', 'DE', 'GB', 'FR', 'RU', 'CA', 'IT', 'AU'],
                  indicators: list[str] = ['GDP', 'POP', 'GDPYY', 'INTR', 'IRYY', 'UR', 'CAG', 'GDG']):
    all_indicators = [f'ECONOMICS:{x}{y}' for x in countries for y in indicators]
    result = defaultdict(defaultdict)

    def on_message(ws, message):
        nonlocal result
        messages = re.split(r'~m~\d{1,7}~m~', message)[1:]

        def cum_data(res_iter):
            nonlocal result
            res_iter = json.loads(res_iter)
            if res_iter['m'] != 'qsd':
                return
            res_iter = res_iter['p'][1]
            indicator = res_iter['n']
            field = res_iter['v']['short_name'] if 'short_name' in res_iter['v'].keys() else None
            value = res_iter['v']['lp'] if 'lp' in res_iter['v'].keys() else None
            desc = res_iter['v']['description'] if 'description' in res_iter['v'].keys() else None
            change = res_iter['v']['ch'] if 'ch' in res_iter['v'].keys() else None
            unit = res_iter['v']['value_unit_id'] if 'value_unit_id' in res_iter['v'].keys() else None
            if field:
                result[indicator]['field'] = field
            if value:
                result[indicator]['value'] = value
            if desc:
                result[indicator]['desc'] = desc
            if change:
                result[indicator]['change'] = change
            if unit:
                result[indicator]['unit'] = unit

        for message_iter in messages:
            cum_data(message_iter)
        messages = pd.DataFrame({k: dict(v) for k, v in dict(result).items()}).T
        messages.dropna(inplace=True, how='any', subset=['field'])
        if len(messages) == len(all_indicators):
            messages.to_sql(con=sqlite3.connect('econ_live.db'), if_exists='replace', index=False, name='live')
            ws.close()

    def on_open(ws):
        print("Connection opened")
        # 发送消息
        # noinspection SpellCheckingInspection
        payload = ["qs_Xn90P2uiDHrm"] + all_indicators
        payload = '{"m":"quote_add_symbols","p":["' + '","'.join(payload) + '"]}'
        payload_length = len(payload)
        messages = [
            '~m~36~m~{"m":"set_data_quality","p":["low"]}',
            '~m~54~m~{"m":"set_auth_token","p":["unauthorized_user_token"]}',
            '~m~34~m~{"m":"set_locale","p":["en","US"]}',
            '~m~52~m~{"m":"quote_create_session","p":["qs_Xn90P2uiDHrm"]}',
            '~m~453~m~{"m":"quote_set_fields","p":["qs_Xn90P2uiDHrm","base-currency-logoid","ch","chp","currency-logoid","currency_code","currency_id","base_currency_id","current_session","description","exchange","format","fractional","is_tradable","language","local_description","listed_exchange","logoid","lp","lp_time","minmov","minmove2","original_name","pricescale","pro_name","short_name","type","typespecs","update_mode","volume","variable_tick_size","value_unit_id"]}',
            f'~m~{payload_length}~m~{payload}'
        ]
        for msg in messages:
            ws.send(msg)

    websocket.enableTrace(False)
    today = datetime.datetime.now()
    ws_instance = websocket.WebSocketApp(
        f"wss://data.tradingview.com/socket.io/websocket?from=markets%2Fworld-economy%2F&date={today.strftime('%Y_%m_%d')}-11_22",
        on_message=on_message, on_open=on_open)
    ws_instance.run_forever()


if __name__ == "__main__":
    get_econ_data()

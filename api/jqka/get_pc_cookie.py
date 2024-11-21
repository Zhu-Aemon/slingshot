"""
生成同花顺所用的v cookie
"""
import execjs


def get_cookie_pc():
    with open('pc_cookie.js', encoding='utf8') as f:
        js_func = execjs.compile(f.read())

    v = js_func.call('getCookie')
    return v.split(';')[0][2:]

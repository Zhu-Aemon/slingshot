"""
生成同花顺所用的v cookie
"""
import execjs


def get_cookie_pc():
    with open('../../js/jqka_v.js', encoding='utf8') as f:
        js_func = execjs.compile(f.read())

    v = js_func.call('get_v')
    return v


if __name__ == '__main__':
    print(get_cookie_pc())

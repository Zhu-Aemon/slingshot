"""
生成同花顺所用的v cookie
"""
import execjs
import os


def get_cookie_pc():
    # Get the absolute path to this file's directory
    module_dir = os.path.dirname(os.path.abspath(__file__))
    # Construct the path to your .js file relative to this Python file
    js_path = os.path.join(module_dir, 'js/jqka_v.js')

    with open(js_path, encoding='utf8') as f:
        js_func = execjs.compile(f.read())

    v = js_func.call('get_v')
    return v


if __name__ == '__main__':
    print(get_cookie_pc())

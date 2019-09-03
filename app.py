import json
import re

from flask import Flask, request

from DFAFilter import DFAFilter
from constants import EXCLUDE_KEY, URL_PATTERN

app = Flask(__name__)

gfw = DFAFilter()
path = "./static/no_distinct_words.csv"
gfw.parse(path)


@app.route('/', methods=['POST', 'GET'])
def filter_words():
    if request.method == 'GET':
        return "欢迎使用敏感词过敏器"
    elif request.method == "POST":
        print("过滤前：", request.json)
        data = request.json
        if isinstance(data, dict):
            gfw.dict_res(data)
        # elif isinstance(data, list):
        #     gfw.list_res(data)
        # elif isinstance(data, str):
        #     gfw.str_res(data)
        print("过滤后：", data)
        return data


# @app.route('/', methods=['POST', 'GET'])
# def filter_words():
#     if request.method == 'GET':
#         return "欢迎使用敏感词过敏器"
#     elif request.method == "POST":
#         print("过滤前：", request.json)
#         data = request.json
#         for k, v in data.items():
#             if k in EXCLUDE_KEY:  # 排除关键字
#                 data[k] = v
#                 continue
#             elif isinstance(v, list):
#                 for index, item in enumerate(v):
#                     if isinstance(item, dict):
#                         for x, y in item.items():
#                             data[k][index][x] = gfw.filter(y)
#             elif isinstance(v, str):
#                 res = re.findall(URL_PATTERN, v)
#                 if res and "media" in res[0][2]:  # 排除静态资源
#                     data[k] = v
#                     continue
#                 elif res and "media" not in res[0][2]:
#                     res = res[0][0] + gfw.filter(res[0][2])
#                     data[k] = res
#                     continue
#             data[k] = gfw.filter(v)
#         print("过滤后：", data)
#         return data


if __name__ == '__main__':
    # text = "天安门事件，港独，台独，还有什么敏感词！"
    # result = gfw.filter(text)
    from werkzeug.contrib.fixers import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app)
    app.run(host="0.0.0.0", port=5000)

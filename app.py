import json

from flask import Flask, request

app = Flask(__name__)


@app.route('/', methods=['POST', 'GET'])
def filter_words():
    if request.method == 'GET':
        return "欢迎使用敏感词过敏器"
    elif request.method == "POST":
        print(request.json)
        data = request.json
        for k, v in data.items():
            data[k] = gfw.filter(v)
        return data


# DFA算法
class DFAFilter(object):
    def __init__(self):
        self.keyword_chains = {}  # 关键词链表
        self.delimit = '\x00'  # 限定

    def add(self, keyword):
        keyword = keyword.lower()  # 关键词英文变为小写
        chars = keyword.strip()  # 关键字去除首尾空格和换行
        if not chars:  # 如果关键词为空直接返回
            return
        level = self.keyword_chains   # level = {}
        # 遍历关键字的每个字
        for i in range(len(chars)):
            # 如果这个字已经存在字符链的key中就进入其子链
            if chars[i] in level:
                level = level[chars[i]]
            else:
                if not isinstance(level, dict):
                    break
                for j in range(i, len(chars)):
                    level[chars[j]] = {}
                    last_level, last_char = level, chars[j]
                    level = level[chars[j]]
                last_level[last_char] = {self.delimit: 0}
                break
        if i == len(chars) - 1:
            level[self.delimit] = 0

    def parse(self, path):
        with open(path, encoding='utf-8') as f:
            for keyword in f:
                self.add(str(keyword).strip())
        # print(self.keyword_chains)

    def filter(self, message, repl="*"):
        if isinstance(message, list):
            return message
        elif isinstance(message, int):
            return message
        message = message.lower()
        ret = []
        start = 0
        while start < len(message):
            level = self.keyword_chains
            step_ins = 0
            for char in message[start:]:
                if char in level:           # 敏感词，在链中
                    step_ins += 1
                    if self.delimit not in level[char]:     # 未到\x00
                        level = level[char]                 # 进入子链
                    else:
                        ret.append(repl * step_ins)         # 计算数量
                        start += step_ins - 1
                        break
                else:
                    ret.append(message[start])
                    break
            else:
                ret.append(message[start])          # 无敏感词
            start += 1

        return ''.join(ret)


gfw = DFAFilter()
path = "./static/no_distinct_words.csv"
gfw.parse(path)

if __name__ == '__main__':
    # text = "天安门事件，港独，台独，还有什么敏感词！"
    # result = gfw.filter(text)
    app.run(host="0.0.0.0", port=5000)

# _*_ encoding:utf-8 _*_
import re

__author__ = 'nzb'
__datetime__ = '2019/9/3 9:26'

from MySQLdb.converters import NoneType

from constants import EXCLUDE_KEY, URL_PATTERN


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
        # if isinstance(message, list):
        #     return message
        # elif isinstance(message, int):
        #     return message
        # if isinstance(message, dict):       # 字段递归调用
        #     for k, v in message.items():
        #         if k in EXCLUDE_KEY:        # 排除关键字
        #             message[k] = v
        #             continue
        #         elif isinstance(v, str):
        #             res = re.findall(URL_PATTERN, v)
        #             if res and "media" in res[0][2]:        # 排除静态资源
        #                 message[k] = v
        #                 continue
        #             elif res and "media" not in res[0][2]:  # 过滤用户自定义的url
        #                 res = res[0][0] + self.filter(res[0][2])
        #                 message[k] = res
        #                 continue
        #         message[k] = self.filter(v)
        #     return message
        # elif isinstance(message, NoneType):
        #     return message
        message = message.lower()
        ret = []
        start = 0
        while start < len(message):
            level = self.keyword_chains
            step_ins = 0
            for char in message[start:]:
                if char in level:                           # 敏感词，在链中
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
                ret.append(message[start])                  # 无敏感词
            start += 1

        return ''.join(ret)

    def list_res(self, result):
        for index, value in enumerate(result):
            if isinstance(value, dict):
                result[index] = self.dict_res(value)
            elif isinstance(value, str):
                result[index] = self.str_res(value)
            elif isinstance(value, int):
                result[index] = value
            elif isinstance(value, list):
                result[index] = self.list_res(value)
        return result

    # def int_res(self, result):
    #     return result

    def str_res(self, result):
        if result == '':
            return ''
        res = re.findall(URL_PATTERN, result)
        if res and "media" in res[0][2]:  # 排除静态资源
            ret = result
        elif res and "media" not in res[0][2]:  # 过滤用户自定义的url
            ret = res[0][0] + self.filter(res[0][2])
        else:
            ret = self.filter(result)
        return ret

    def dict_res(self, result):
        for k, v in result.items():
            if k in EXCLUDE_KEY:  # 排除关键字
                result[k] = v
                continue
            elif isinstance(v, str):
                result[k] = self.str_res(v)
            elif isinstance(v, list):
                result[k] = self.list_res(v)
            elif isinstance(v, int):
                result[k] = v
            elif isinstance(v, dict):
                result[k] = self.dict_res(v)
        return result

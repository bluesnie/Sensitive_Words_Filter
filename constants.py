# _*_ encoding:utf-8 _*_
import re

__author__ = 'nzb'
__datetime__ = '2019/9/3 9:29'

EXCLUDE_KEY = ('code', 'errMsg', 'next', 'previous', 'count', 'id', 'avatar', 'school', 'creator_role', 'address', 'create_time')
URL_PATTERN = re.compile('(http(s)?://)(.*)')





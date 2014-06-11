#!/usr/bin/env python
# -*- coding: utf-8 -*-

from random import choice
from string import Template


def _decode(string):
    try:
        string = string.decode('utf-8-sig')
    except UnicodeDecodeError:
        try:
            string = string.decode('utf_16')
        except UnicodeDecodeError:
            string = string.decode('gbk', 'ignore')
    return string


def render(context, template_name):
    """渲染模板，返回渲染结果

    :param context: 模板内使用的变量
    :type context: dict
    :template_name: 模板文件路径列表,
                    从列表中随机选择一个文件进行渲染
    """
    tpl = choice(template_name)
    with open(tpl) as f:
        content = _decode(f.read())
        try:
            result = Template(content).substitute(context)
        except ValueError:
            print(u'模板文件 (%s) 内容格式错误!' % tpl)
            result = Template(content).safe_substitute(context)
    return result


def eval_bool(*args):
    """执行包含布尔操作的字符串"""
    return eval('%s' % (' '.join(map(str, args))), {}, {})


# modified from web.py(http://webpy.org/)
class Storage(dict):
    """
    A Storage object is like a dictionary except `obj.foo` can be used
    in addition to `obj['foo']`.

        >>> o = storage(a=1)
        >>> o.a
        1
        >>> o['a']
        1
        >>> o.a = 2
        >>> o['a']
        2
        >>> del o.a
        >>> o.a
        Traceback (most recent call last):
            ...
        AttributeError: 'a'

    """
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError as k:
            raise AttributeError(k)

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError as k:
            raise AttributeError(k)
storage = Storage


# sandrotosi.blogspot.com/2011/04/python-group-list-in-sub-lists-of-n.html
def group_iter(iterator, n=2, fill=False):
    """| Given an iterator, it returns sub-lists made of n items
    | (except the last that can have len < n)
    | inspired by http://countergram.com/python-group-iterator-list-function

    对列表进行分组：
    list(group_iter([1, 2, 3, 4], 3)) -> [[1, 2, 3], [4]]
    """
    accumulator = []
    for item in iterator:
        accumulator.append(item)
        if len(accumulator) == n:  # tested as fast as separate counter
            yield accumulator
            accumulator = []  # tested faster than accumulator[:] = []
            # and tested as fast as re-using one list object
    if len(accumulator) != 0:
        if fill:
            accumulator += [None] * (n - len(accumulator))
        yield accumulator

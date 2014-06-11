#!/usr/bin/env python
# -*- coding: utf-8 -*-

from random import choice
from string import Template
import time


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


class Retry(object):
    """重试功能"""
    def __init__(self, tries=4, sleep_time=1, ignore_error=False):
        self.ignore_error = ignore_error
        self.tries = tries
        self.sleep_time = sleep_time

    def __call__(self, func, *args, **kwargs):
        _exec = lambda f: f(*args, **kwargs)

        # 首先重试 n-1 次
        for __ in range(self.tries - 1):
            try:
                return _exec()
            except Exception as e:
                print(e)
                time.sleep(self.sleep_time)
        # 最后重试1次
        try:
            return _exec()
        except Exception as e:
            print(e)
            if self.ignore_error:
                return
            else:
                raise


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

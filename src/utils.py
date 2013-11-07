#!/usr/bin/env python
# -*- coding: utf-8 -*-


def eval_bool(*args):
    """ 执行包含布尔操作的字符串 """
    return eval('%s' % (' '.join(map(str, args))), {"__builtins__": None}, {})

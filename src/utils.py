#!/usr/bin/env python
# -*- coding: utf-8 -*-


def eval_bool(*args):
    """ 执行包含布尔操作的字符串 """
    return eval('%s' % (' '.join(map(str, args))), {"__builtins__": None}, {})


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

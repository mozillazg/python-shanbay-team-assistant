#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from getpass import getpass
import sys

from src.shanbay import Shanbay

username = raw_input('\nUsername: ')
password = getpass()
shanbay = Shanbay(username, password)
encoding = sys.stdin.encoding
try:
    input = raw_input
except NameError:
    pass


def test_members():
    """获取小组成员信息"""
    members = shanbay.members()
    print('')
    for member in members:
        print('{id}, {nickname}, {role}, {points}, {days}, {rate}, '\
              '{checked_yesterday}, {checked_today}'.format(**member))
    assert True


def test_dismiss():
    """踢人"""
    members = shanbay.members()
    print('')
    for member in members:
        print('{nickname}: {checked_today}'.format(**member))
        confirm = raw_input('踢除？ (y/n)'.encode(encoding)).strip().lower()
        if confirm.startswith('y'):
            print('成功踢除' if shanbay.dismiss(member['id']) else '剔除失败')

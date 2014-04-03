#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import ConfigParser
from StringIO import StringIO

from .utils import storage


def _decode(string):
    try:
        string = string.decode('utf-8-sig')
    except UnicodeDecodeError:
        string = string.decode('gbk', 'ignore')
    return string


class Setting(object):
    def __init__(self, settings_file='settings.ini'):
        # 读取配置文件
        self.conf = ConfigParser.RawConfigParser()
        with open(settings_file, 'rb') as f:
            content = _decode(f.read()).encode('utf8')
            self.conf.readfp(StringIO(content))

    def _(self, key):
        value = self.conf.get('General', key)
        return _decode(value)

    def settings(self):
        # 小组信息
        team_id = self._('team_id')
        team_url = self._('team_url')

        # 踢人开始时间, 结束时间自然是 00:00
        start_time = self._('start_time')

        username = self._('username')
        password = self._('password')

        # 成员加入条件
        limit = self._('limit')
        default_limit = self._('default_limit')

        # 欢迎     组龄
        welcome = self._('welcome')
        welcome_title = self._('welcome_title')
        # 警告     组龄，打卡率， 当天是否打卡(1: 打卡，0: 不限制是否打卡)
        warnning = map(lambda x: x.strip(), self._('warnning').split(','))
        warnning_title = self._('warnning_title')
        # 踢人     组龄，打卡率， 当天是否打卡
        dismiss = map(lambda x: x.strip(), self._('dismiss').split(','))
        dismiss_title = self._('dismiss_title')
        # 恭喜          组龄
        congratulate = map(lambda x: int(x.strip()), self._('congratulate').split(','))
        congratulate_title = self._('congratulate_title')

        dismiss_topic_id = self._('dismiss_topic_id')
        grow_up_topic_id = self._('grow_up_topic_id')

        # 确认
        try:
            confirm = bool(int(self._('confirm')))
        except:
            confirm = True

        return storage(locals())

if __name__ == '__main__':
    from pprint import pprint
    settings = Setting().settings()
    pprint(settings)

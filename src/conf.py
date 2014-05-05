#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import ConfigParser
from glob import glob
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

    def get_option(self, key, default=None):
        try:
            value = self.conf.get('General', key)
            return _decode(value)
        except ConfigParser.Error:
            if default is not None:
                return default
            else:
                raise

    def get_option_list(self, key, default=None):
        return map(lambda x: x.strip(), self.get_option(key, default).split(','))

    def get_option_f(self, key, default=None):
        file_path = self.get_option(key, default)
        return glob(file_path)

    def settings(self):
        username = self.get_option('username')
        password = self.get_option('password')

        # 小组信息
        team_id = self.get_option('team_id')
        team_url = self.get_option('team_url')
        
        dismiss_topic_id = self.get_option('dismiss_topic_id')
        dismiss_topic_template = self.get_option_f('dismiss_topic_template', ['dismiss_topic.txt'])
        grow_up_topic_id = self.get_option('grow_up_topic_id')
        grow_up_topic_template = self.get_option_f('grow_up_topic_template', ['grow_up_topic.txt'])

        # 踢人开始时间, 结束时间自然是 00:00
        start_time = self.get_option('start_time')

        # 成员加入条件
        limit = self.get_option('limit', 1000)
        default_limit = self.get_option('default_limit')

        # 欢迎     组龄
        welcome = self.get_option('welcome', 0)
        welcome_title = self.get_option('welcome_title')
        welcome_template = self.get_option_f('welcome_template', ['welcome_mail.txt'])
        # 警告     组龄，打卡率， 当天是否打卡(1: 打卡，0: 不限制是否打卡)
        warnning = self.get_option_list('warnning')
        warnning_title = self.get_option_list('warnning_title')
        warnning_template = self.get_option_f('warnning_template', ['warn_mail.txt'])
        # 踢人     组龄，打卡率， 当天是否打卡
        dismiss = self.get_option_list('dismiss')
        dismiss_title = self.get_option('dismiss_title')
        dismiss_template = self.get_option_f('dismiss_template', ['dismiss_mail.txt'])
        # 恭喜          组龄
        congratulate = self.get_option_list('congratulate')
        congratulate_title = self.get_option('congratulate_title')
        congratulate_template = self.get_option_f('congratulate_template', ['congratulate_mail.txt'])

        # 确认
        try:
            confirm = bool(int(self.get_option('confirm', True)))
        except:
            confirm = True

        return storage(locals())

if __name__ == '__main__':
    from pprint import pprint
    settings = Setting().settings()
    pprint(settings)

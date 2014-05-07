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

    def _get_option(self, key, default=None):
        try:
            value = self.conf.get('General', key)
            return _decode(value)
        except ConfigParser.Error:
            if default is not None:
                return default
            else:
                raise

    def _get_option_list(self, key, default=None):
        return map(lambda x: x.strip(),
                   self._get_option(key, default).split(','))

    def _get_option_f(self, key, default=None):
        file_path = self._get_option(key, default)
        return glob(file_path)

    def settings(self):
        username = self._get_option('username')
        password = self._get_option('password')

        # 小组信息
        team_id = self._get_option('team_id')
        team_url = self._get_option('team_url')

        dismiss_topic_id = self._get_option('dismiss_topic_id')
        dismiss_topic_template = self._get_option_f('dismiss_topic_template',
                                                    ['dismiss_topic.txt'])
        grow_up_topic_id = self._get_option('grow_up_topic_id')
        grow_up_topic_template = self._get_option_f('grow_up_topic_template',
                                                    ['grow_up_topic.txt'])

        # 踢人开始时间
        start_time = self._get_option('start_time')

        # 成员加入条件
        limit = self._get_option('limit', 1000)
        default_limit = self._get_option('default_limit')

        # 欢迎
        welcome = self._get_option('welcome', 0)
        welcome_title = self._get_option('welcome_title')
        welcome_template = self._get_option_f('welcome_template',
                                              ['welcome_mail.txt'])
        # 警告
        warnning = self._get_option_list('warnning')
        warnning_title = self._get_option_list('warnning_title')
        warnning_template = self._get_option_f('warnning_template',
                                               ['warn_mail.txt'])
        # 踢人
        dismiss = self._get_option_list('dismiss')
        dismiss_title = self._get_option('dismiss_title')
        dismiss_template = self._get_option_f('dismiss_template',
                                              ['dismiss_mail.txt'])
        # 恭喜
        congratulate = self._get_option_list('congratulate')
        congratulate_title = self._get_option('congratulate_title')
        congratulate_template = self._get_option_f('congratulate_template',
                                                   ['congratulate_mail.txt'])

        # 确认
        try:
            confirm = bool(int(self._get_option('confirm', True)))
        except:
            confirm = True

        d = locals()
        d.pop('self')
        return storage(d)

if __name__ == '__main__':
    from pprint import pprint
    settings = Setting().settings()
    pprint(settings)

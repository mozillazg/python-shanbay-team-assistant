#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import ConfigParser
from glob import glob as _glob
from os.path import realpath
from StringIO import StringIO

from utils import storage, _decode
import datetime

glob = lambda f: map(realpath, _glob(f))


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

    def _get_option_bool(self, key, default):
        try:
            return bool(int(self._get_option(key, default)))
        except:
            return default

    def _get_option_multi_line(self, key, default):
        s = self._get_option(key, default)
        return s.split()

    def _get_option_multi_line_f(self, key, default):
        lst = self._get_option_multi_line(key, default)
        return reduce(lambda x, y: x + y, map(glob, lst))

    def _split_condition(self, condition):
        checked_yesterday = None
        check_list = [x.strip() for x in condition.split(':')]
        try:
            days, rate, checked, points, checked_yesterday = check_list
        except ValueError:  # 兼容旧的配置文件
            days, rate, checked, points = check_list
        return days, rate, checked, points, checked_yesterday

    def settings(self):
        username = self._get_option('username')
        password = self._get_option('password')

        # 小组信息
        team_id = self._get_option('team_id')
        team_url = self._get_option('team_url')

        dismiss_topic_id = self._get_option('dismiss_topic_id')
        dismiss_topic_template = self._get_option_f('dismiss_topic_template',
                                                    ['dismiss_topic.txt'])
        update_dismiss_topic = self._get_option_bool('update_dismiss_topic', True)

        grow_up_topic_id = self._get_option('grow_up_topic_id')
        grow_up_topic_template = self._get_option_f('grow_up_topic_template',
                                                    ['grow_up_topic.txt'])
        update_grow_up_topic = self._get_option_bool('update_grow_up_topic', True)

        # 踢人开始时间
        start_time = self._get_option('start_time')
        start_time = datetime.datetime.strptime(start_time, '%H:%M').time()

        # 成员加入条件
        limit = self._get_option('limit', 1000)
        default_limit = self._get_option('default_limit')

        # 欢迎
        welcome = self._get_option('welcome', '<=0')
        welcome_title = self._get_option('welcome_title')
        welcome_template = self._get_option_multi_line_f('welcome_template',
                                                         ['welcome_mail.txt'])
        # 警告
        warnning = map(self._split_condition,
                       self._get_option_list('warnning'))
        warnning_title = self._get_option('warnning_title')
        warnning_template = self._get_option_multi_line_f('warnning_template',
                                                          ['warn_mail.txt'])
        # 踢人
        dismiss = map(self._split_condition, self._get_option_list('dismiss'))
        dismiss_title = self._get_option('dismiss_title')
        dismiss_template = self._get_option_multi_line_f('dismiss_template',
                                                         ['dismiss_mail.txt'])
        # 恭喜
        congratulate = map(int, self._get_option_list('congratulate'))
        congratulate_title = self._get_option('congratulate_title')
        congratulate_template = self._get_option_multi_line_f('congratulate_template',
                                                              ['congratulate_mail.txt'])
        template_order = self._get_option_bool('template_order', False)

        # 询问
        confirm = self._get_option_bool('confirm', True)

        d = locals()
        d.pop('self')
        return storage(d)

if __name__ == '__main__':
    from pprint import pprint
    settings = Setting().settings()
    pprint(settings)

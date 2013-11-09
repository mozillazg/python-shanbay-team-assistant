#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import ConfigParser

# 读取配置文件
conf = ConfigParser.RawConfigParser()
conf.read('settings.ini')

_ = lambda key: conf.get('General', key)

# 小组信息
team_id = _('team_id')
team_url = _('team_url')

# 踢人开始时间, 结束时间自然是 00:00
start_time = _('start_time')

username = _('username')
password = _('password')

# 成员加入条件
limit = _('limit')
default_limit = _('default_limit')

# 欢迎     组龄
welcome = _('welcome')
welcome_title = _('welcome_title')
# 警告     组龄，打卡率， 当天是否打卡(1: 打卡，0: 不限制是否打卡)
warnning = _('warnning')
warnning_title = _('warnning_title')
# 踢人     组龄，打卡率， 当天是否打卡
dismiss = map(lambda x: x.strip(), _('dismiss').split(','))
dismiss_title = _('dismiss_title')
# 恭喜          组龄
congratulate = map(lambda x: int(x.strip()), _('congratulate').split(','))
congratulate_title = _('congratulate_title')

dismiss_topic_id = _('dismiss_topic_id')
grow_up_topic_id = _('grow_up_topic_id')

if __name__ == '__main__':
    print(locals())

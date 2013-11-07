#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
from getpass import getpass
import os
from string import Template
import sys

import settings
from shanbay import Shanbay
from utils import eval_bool

try:
    input = raw_input
except NameError:
    pass
encoding = sys.stdin.encoding

def output_member_info(member):
    print(u'{nickname}, 组龄: {days} 打卡率: {rate}% 今天是否打卡: '
          ''.format(**member) + (u'是' if member['checked'] else u'否'))


def confirm(msg):
    return input(msg.encode(encoding)).strip().lower().startswith('y')


def render(context, template_name):
    with open(template_name) as f:
        result = Template(f.read()).substitute(context)
    return result

username = settings.username or input('Username: ')
password = settings.password or getpass()

shanbay = Shanbay(username, password, settings.team_id, settings.team_url)

# 判断当前时间
current_time = shanbay.server_date().time()
start_time = datetime.datetime.strptime(settings.start_time, '%H:%M').time()
if current_time < start_time:
    print(u'时间还早者呢，请 {0} 后再操作!'.format(settings.start_time))
    os._exit(1)

# print(' 开始 '.center(78, '#'))

# 设置加入条件
limit = settings.limit
print(u'设置小组成员加入条件为：打卡天数>={0}'.format(limit))
shanbay.update_limit(limit)

# 获取成员信息
all_members = []
new_members = []       # 新人
warnning_members = []  # 警告
dismiss_members = []   # 踢人
max_page = shanbay.max_page(shanbay.dismiss_url)
for page in range(1, max_page + 1):
    print(u'第%s页' % page)
    url = '%s?page=%s' % (shanbay.dismiss_url, page)
    members = shanbay.single_page_members(url)
    all_members.extend(members)
    # 对成员进行操作
    for member in members:
        # 新人
        if eval_bool(member['days'], settings.welcome):
            output_member_info(member)
            if confirm(u'是否发送欢迎短信? (y/n)'):
                if shanbay.send_mail([member['username']], 'welcome',
                                     render(member, 'welcome_mail.txt')):
 
                    print(u'短信已发送')
                else:
                    print(u'短信发送失败')
            new_members.append(member)

        # 踢人
        condition_bool = False
        for condition in settings.dismiss:
            days, rate, checked = condition.split(':')
            bool_ = True
            if days:
                bool_ = bool_ and eval_bool(member['days'], days)
            if rate:
                bool_ = bool_ and eval_bool(member['rate'], rate)
            if not int(checked):
                bool_ = bool_ and (not member['checked'])
            condition_bool = condition_bool or bool_
        print condition_bool
        if condition_bool:
            output_member_info(member)
            if confirm(u'是否发送踢人短信? (y/n)'):
                if shanbay.send_mail([member['username']], 'dismiss',
                                     render(member, 'dismiss_mail.txt')):
 
                    print(u'短信已发送')
                    print(u'已执行踢除操作')
                    shanbay.dismiss(member.id)
                else:
                    print(u'短信发送失败')
                dismiss_members.append(member)

        # 警告
        conditions = settings.warnning.split(':')
        days, rate, checked = conditions
        condition_bool = True
        if days:
            condition_bool = condition_bool and eval_bool(member['days'], days)
        if rate:
            condition_bool = condition_bool and eval_bool(member['rate'], rate)
        if not int(checked):
            condition_bool = condition_bool and (not member['checked'])
        if condition_bool:
            output_member_info(member)
            if confirm(u'是否发送警告短信? (y/n)'):
                if shanbay.send_mail([member['username']], 'warnning',
                                     render(member, 'warn_mail.txt')):
 
                    print(u'短信已发送')
                else:
                    print(u'短信发送失败')
            warnning_members.append(member)

        # 恭喜
        for days in settings.congratulate:
            if member['days'] == days:
                output_member_info(member)
                if confirm(u'是否发送恭喜短信? (y/n)'):
                    if shanbay.send_mail([member['username']], 'congratulation',
                                         render(member, 'congratulate_mail.txt')):
                        print(u'短信已发送')
                    else:
                        print(u'短信发送失败')

print(members)
print(len(members))
print(new_members)
print(warnning_members)
print(dismiss_members)

print(u'更新查卡贴')
context = {
    'today': shanbay.server_date().strftime('%Y-%m-%d'),
    'number': len(dismiss_members)
}
content = render(context, 'dismiss_topic.txt')
shanbay.reply_topic(251953, content)

print(u'更新小组数据贴')
content = render(shanbay.team_info(), 'grow_up_topic.txt')
shanbay.reply_topic(251950, content)

print(u'设置小组成员加入条件为：打卡天数>=0')
shanbay.update_limit(0)

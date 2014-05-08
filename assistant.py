#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""扇贝网小组管理助手"""

__version__ = '0.1.6.dev'
__author__ = 'mozillazg'
__license__ = 'MIT'
__copyright__ = 'Copyright (c) 2014 mozillazg'

import datetime
from getpass import getpass
import logging
from random import choice
from string import Template
import sys
import time

from argparse import ArgumentParser
from shanbay import Shanbay, AuthException

from conf import Setting
from utils import eval_bool, _decode

try:
    input = raw_input
except NameError:
    pass
encoding = sys.stdin.encoding

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('debug.log')
formatter = logging.Formatter('%(asctime)s - %(name)s '
                              '- %(funcName)s - %(lineno)d - %(levelname)s -'
                              ' %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

sleep_time = 1
settings = None
shanbay = None
team = None
message = None


def parse_conf():
    parser = ArgumentParser()
    parser.add_argument('-V', '--version', action='version',
                        version=__version__)
    parser.add_argument('-i', '--interactive', action='store_true',
                        help='prompt before exec action')
    parser.add_argument('-s', '--settings',
                        help='settings file (default: settings.ini)',
                        default='settings.ini')
    parser.add_argument('-a', '--announce', required=False,
                        help='send announcement to all members (an text file)')
    parser.add_argument('-t', '--title', default='announce',
                        help='announcement title (default: announce)')

    args = parser.parse_args()
    settings = Setting(args.settings).settings()
    settings.confirm = args.interactive or settings.confirm
    announce_file = args.announce
    announce_title = args.title.decode(sys.stdin.encoding)
    return {
        'settings': settings,
        'announce_file': announce_file,
        'announce_title': announce_title
    }


def output_member_info(member):
    """输出组员信息"""
    print((u'用户名: {username:<10} 昵称: {nickname:<20} 组龄: {days:<5}'
           u' 贡献值成长值：{points:<8}'.format(**member)
           + u' 打卡率: {rate}%'.format(**member).ljust(15)
           + u' 昨天是否打卡: '
           + (u'是' if member['checked_yesterday'] else u'否')
           + u'    今天是否打卡：'
           + (u'是' if member['checked'] else u'否')
           ).encode(encoding, 'ignore')
          )


def confirm(msg):
    """提示信息"""
    while True:
        if not settings.confirm:
            print(msg + 'y')
            time.sleep(sleep_time)
            return True
        c = input(msg.encode(encoding)).strip().lower()
        if c == 'y':
            return True
        elif c == 'n':
            return False


def render(context, template_name):
    """渲染模板，返回渲染结果"""
    tpl = choice(template_name)
    with open(tpl) as f:
        content = _decode(f.read())
        result = Template(content).substitute(context)
    return result


def retry_shanbay(shanbay_method, ignore=False, catch='exception',
                  *args, **kwargs):
    """重试功能, catch: exception, bool"""
    n = 3
    t = 1

    def _exec():
        result = shanbay_method(*args, **kwargs)
        if catch == 'bool':
            assert result
        return result

    # 首先重试n次
    for __ in range(n):
        try:
            return _exec()
            break
        except Exception as e:
            print(e)
            time.sleep(t)
    else:
        # 最后1重试次
        try:
            return _exec()
        except Exception as e:
            print(e)
            if ignore:
                print(u'exec %s fail' % shanbay_method)
                return
            else:
                raise


def check_time():
    """检查是否到了可以查卡的时间"""
    # 服务器时间
    current_datetime = retry_shanbay(lambda: shanbay.server_date, False, 'exception')
    current_time = current_datetime.time()
    # 查卡时间
    start_time = datetime.datetime.strptime(settings.start_time, '%H:%M').time()
    if current_time < start_time:
        print(u'时间还早者呢，请 {0} 后再操作!'.format(settings.start_time))
        if confirm(u'设置小组成员加入条件为：打卡天数>=%s (y/n) ' %
                   settings.default_limit):
            if retry_shanbay(team.update_limit, False, 'bool',
                             settings.default_limit):
                print(u'设置更新成功')
            else:
                print(u'设置更新失败')
        sys.exit(0)
    else:
        return current_datetime


def get_all_members(max_page):
    """获取所有成员信息"""
    all_members = []
    for page in range(1, max_page + 1):
        print(u'获取第%s页的所有成员' % page)
        members = retry_shanbay(team.single_page_members, False,
                                'exception', page)
        all_members.extend(members)
        print(u'%s人' % len(members))
        time.sleep(sleep_time)

    print(u'total: %s人' % len(all_members))
    return all_members


def check_welcome(member, settings):
    """检查是否是新人"""
    if eval_bool(member['days'], settings.welcome):
        if retry_shanbay(message, True, 'bool',
                         [member['username']], settings.welcome_title,
                         render(member, settings.welcome_template)):

            print(u'欢迎短信已发送')
        else:
            print(u'欢迎短信发送失败')
        return member


def check_congratulate(member, settings):
    """恭喜"""
    for days in settings.congratulate:
        if member['days'] == days:
            if retry_shanbay(message, True, 'bool',
                             [member['username']],
                             settings.congratulate_title,
                             render(member, settings.congratulate_template)):
                print(u'恭喜短信已发送')
            else:
                print(u'恭喜短信发送失败')
            return member


def _check_condition(conditions, member):
    condition_bool = False
    # 检查是否满足条件
    for condition in conditions:
        checked_yesterday = None
        check_list = [x.strip() for x in condition.split(':')]
        try:
            days, rate, checked, points, checked_yesterday = check_list
        except ValueError:
            days, rate, checked, points = check_list

        bool_ = True
        if days:  # 组龄
            bool_ = bool_ and eval_bool(member['days'], days)
        if rate:  # 打卡率
            bool_ = bool_ and eval_bool(member['rate'], rate)
        if points:  # 贡献值
            bool_ = bool_ and eval_bool(member['points'], points)
        if checked and (not int(checked)):  # 当天未打卡
            bool_ = bool_ and (not member['checked'])
        if checked_yesterday and (not int(checked_yesterday)):  # 昨天未打卡
            bool_ = bool_ and (not member['checked_yesterday'])

        condition_bool = condition_bool or bool_
        if condition_bool:
            break

    return condition_bool


def check_dismiss(member, settings):
    """踢人"""
    condition_bool = _check_condition(settings.dismiss, member)
    if not condition_bool:
        return

    if confirm(u'是否踢人并发送踢人短信? (y/n) '):
        if retry_shanbay(team.dismiss, False, 'bool', member['id']):
            print(u'已执行踢人操作')
            if retry_shanbay(message, True, 'bool',
                             [member['username']], settings.dismiss_title,
                             render(member, settings.dismiss_template)):

                print(u'踢人短信已发送')
            else:
                print(u'踢人短信发送失败')
        else:
            print(u'踢人失败')
        return member


def check_warnning(member, settings):
    """警告"""
    condition_bool = _check_condition(settings.warnning, member)
    if not condition_bool:
        return

    if confirm(u'是否发送警告短信? (y/n) '):
        if retry_shanbay(message, True, 'bool',
                         [member['username']],
                         settings.warnning_title,
                         render(member, settings.warnning_template)):

            print(u'警告短信已发送')
        else:
            print(u'警告短信发送失败')
        return member


def announce(all_members, announce_file, announce_title):
    """给所有组员发送通知短信"""
    if not confirm(u'确定要给所有组员发送通知短信？ (y/n)'):
        sys.exit(0)

    for member in all_members:
        msg = render(member, [announce_file])
        if retry_shanbay(message, True, 'bool',
                         [member['username']], announce_title, msg):
            print((u'成功通知 %s' % member['nickname']
                   ).encode(encoding, 'ignore'))
        else:
            print(u'通知发送失败!')


def main():
    global settings
    global shanbay
    global team
    global message

    conf = parse_conf()
    settings = conf['settings']
    announce_file = conf['announce_file']
    announce_title = conf['announce_title']

    # 登录
    username = settings.username or input('Username: ').decode(encoding).strip()
    password = settings.password or getpass()
    shanbay = retry_shanbay(Shanbay, False, 'exception', username, password)
    retry_shanbay(shanbay.login, False, 'exception')
    team = shanbay.team(settings.team_url)
    message = shanbay.message

    if not announce_file:
        # 判断当前时间
        current_datetime = check_time()

    # 获取成员信息
    new_members = []       # 新人
    warnning_members = []  # 警告
    dismiss_members = []   # 踢人
    max_page = retry_shanbay(lambda: team.max_page, False, 'exception')
    all_members = get_all_members(max_page)

    # 给全体组员发短信
    if announce_file:
        announce(all_members, announce_file, announce_title)
        sys.exit(0)

    # 设置加入条件
    limit = settings.limit

    if confirm(u'\n设置小组成员加入条件为：打卡天数>={0} (y/n) '.format(limit)):
        if retry_shanbay(team.update_limit, False, 'bool', limit):
            print(u'设置更新成功')
        else:
            print(u'设置更新失败')

    # 对所有成员进行操作
    print(u'\n开始对所有成员进行处理')
    for member in all_members:
        output_member_info(member)
        if member['username'].lower() == username.lower():
            continue

        # 新人
        if check_welcome(member, settings):
            new_members.append(member)

        # 恭喜
        check_congratulate(member, settings)

        # 踢人
        if check_dismiss(member, settings):
            dismiss_members.append(member)
            continue

        if check_warnning(member, settings):
            # 警告
            warnning_members.append(member)

    print(u'\n被踢:')
    for x in dismiss_members:
        output_member_info(x)

    if confirm(u'\n更新查卡贴 (y/n)'):
        context = {
            'today': current_datetime.strftime('%Y-%m-%d'),
            'number': len(dismiss_members)
        }
        content = render(context, settings.dismiss_topic_template)
        if not settings.confirm:
            print(content)
        if retry_shanbay(team.reply_topic, False, 'bool',
                         settings.dismiss_topic_id, content):
            print(u'帖子更新成功')
        else:
            print(u'帖子更新失败')

    if confirm(u'\n更新小组数据贴 (y/n) '):
        context = retry_shanbay(lambda: team.info, False, 'exception')
        context['today'] = current_datetime.strftime('%Y-%m-%d')
        content = render(context, settings.grow_up_topic_template)
        if not settings.confirm:
            print(content)
        if retry_shanbay(team.reply_topic, False, 'bool',
                         settings.grow_up_topic_id, content):
            print(u'帖子更新成功')
        else:
            print(u'帖子更新失败')

    if confirm(u'\n设置小组成员加入条件为：打卡天数>=%s (y/n) '
               % settings.default_limit):
        if retry_shanbay(team.update_limit, False, 'bool',
                         settings.default_limit):
            print(u'设置更新成功')
        else:
            print(u'设置更新失败')

if __name__ == '__main__':
    print(u'版本：%s\n' % __version__)
    while True:
        try:
            main()
        except AuthException:
            print(u'登录失败')
        except (EOFError, KeyboardInterrupt):
            sys.exit(0)
        except Exception as e:
            print(u'程序运行中出现错误了: %s' % e)
            logger.exception('')
            sys.exit(e)
        if confirm(u'\n退出? (y/n) '):
            break
        print('\n')

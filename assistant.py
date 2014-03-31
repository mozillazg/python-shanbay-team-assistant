#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = '0.1.3'

import datetime
from getpass import getpass
import logging
from string import Template
import sys
import time

from src import settings
from src.shanbay import LoginException
from src.shanbay import Shanbay
from src.utils import eval_bool

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


def output_member_info(member):
    """输出组员打卡信息"""
    print((u'{nickname} 组龄: {days} 贡献值成长值：{points} '
           u'打卡率: {rate}% 昨天是否打卡: ' ''.format(**member)
           + (u'是' if member['checked_yesterday'] else u'否')
           + u' 今天是否打卡：'
           + (u'是' if member['checked'] else u'否')
           ).encode(encoding, 'ignore')
          )


def confirm(msg):
    """提示信息"""
    while True:
        if not settings.confirm:
            print(msg)
            time.sleep(5)
            return True
        c = input(msg.encode(encoding)).strip().lower()
        if c == 'y':
            return True
        elif c == 'n':
            return False


def render(context, template_name):
    """渲染模板，返回渲染结果"""
    with open(template_name) as f:
        content = f.read()
        try:
            content = content.decode('utf-8-sig')
        except UnicodeDecodeError:
            content = content.decode('gbk', 'ignore')
        result = Template(content).substitute(context)
    return result


def retry_shanbay(shanbay_method, ignore=False, catch='exception',
                  *args, **kwargs):
    """重试功能, catch: exception, bool"""
    n = 5
    t = 5

    def _exec():
        result = shanbay_method(*args, **kwargs)
        if catch == 'bool':
            assert result
        return result

    # 首先重试5次
    for __ in range(n):
        try:
            return _exec()
            break
        except:
            time.sleep(t)
    else:
        # 最后1重试次
        try:
            return _exec()
        except Exception as e:
            if ignore:
                print(u'exec %s fail' % shanbay_method)
                return
            else:
                raise


def check_time(shanbay, settings):
    """检查是否到了可以查卡的时间"""
    # 服务器时间
    current_datetime = retry_shanbay(shanbay.server_date, False, 'exception')
    current_time = current_datetime.time()
    # 查卡时间
    start_time = datetime.datetime.strptime(settings.start_time, '%H:%M').time()
    if current_time < start_time:
        print(u'时间还早者呢，请 {0} 后再操作!'.format(settings.start_time))
        if confirm(u'设置小组成员加入条件为：打卡天数>=%s (y/n) ' %
                   settings.default_limit):
            if retry_shanbay(shanbay.update_limit, False, 'bool',
                             settings.default_limit):
                print(u'设置更新成功')
            else:
                print(u'设置更新失败')
        sys.exit(0)
    else:
        return current_datetime


def get_all_members(shanbay, max_page):
    """获取所有成员信息"""
    all_members = []
    for page in range(1, max_page + 1):
        print(u'获取第%s页的所有成员' % page)
        url = '%s?page=%s' % (shanbay.dismiss_url, page)
        members = retry_shanbay(shanbay.single_page_members, False,
                                'exception', url)
        all_members.extend(members)
        if not settings.confirm:
            print(u'%s人' % len(members))
        time.sleep(5)

    if not settings.confirm:
        print(u'total: %s人' % len(all_members))
    return all_members


def check_welcome(shanbay, member, settings):
    """检查是否是新人"""
    if eval_bool(member['days'], settings.welcome):
        if retry_shanbay(shanbay.send_mail, True, 'bool',
                         [member['username']], settings.welcome_title,
                         render(member, 'welcome_mail.txt')):

            print(u'欢迎短信已发送')
        else:
            print(u'欢迎短信发送失败')
        return member


def check_congratulate(shanbay, member, settings):
    """恭喜"""
    for days in settings.congratulate:
        if member['days'] == days:
            if retry_shanbay(shanbay.send_mail, True, 'bool',
                             [member['username']],
                             settings.congratulate_title,
                             render(member, 'congratulate_mail.txt')):
                print(u'恭喜短信已发送')
            else:
                print(u'恭喜短信发送失败')
            return member


def _check_condition(conditions):
    condition_bool = False
    # 检查是否满足条件
    for condition in conditions:
        days, rate, checked, points = condition.split(':')
        bool_ = True
        if days:  # 组龄
            bool_ = bool_ and eval_bool(member['days'], days)
        if rate:  # 打卡率
            bool_ = bool_ and eval_bool(member['rate'], rate)
        if points:  # 贡献值
            bool_ = bool_ and eval_bool(member['points'], points)
        if checked and not int(checked):  # 当天未打卡
            bool_ = bool_ and (not member['checked'])
        condition_bool = condition_bool or bool_
        if condition_bool:
            break

    return condition_bool


def check_dismiss(shanbay, member, settings):
    """踢人"""
    condition_bool = False
    # 检查踢人条件
    for condition in settings.dismiss:
        days, rate, checked, points = condition.split(':')
        bool_ = True
        if days:  # 组龄
            bool_ = bool_ and eval_bool(member['days'], days)
        if rate:  # 打卡率
            bool_ = bool_ and eval_bool(member['rate'], rate)
        if points:  # 贡献值
            bool_ = bool_ and eval_bool(member['points'], points)
        if checked and not int(checked):  # 当天未打卡
            bool_ = bool_ and (not member['checked'])
        condition_bool = condition_bool or bool_
        if condition_bool:
            break

    if not condition_bool:
        return

    if confirm(u'是否发送踢人短信并踢人? (y/n) '):
        if retry_shanbay(shanbay.dismiss, False, 'bool', member['id']):
            print(u'已执行踢人操作')
            if retry_shanbay(shanbay.send_mail, True, 'bool',
                             [member['username']], settings.dismiss_title,
                             render(member, 'dismiss_mail.txt')):

                print(u'踢人短信已发送')
            else:
                print(u'踢人短信发送失败')
        else:
            print(u'踢人失败')
        return member


def check_warnning(shanbay, member, settings):
    """警告"""
    conditions = settings.warnning.split(':')
    days, rate, checked, points = conditions
    condition_bool = True
    if days:
        condition_bool = condition_bool and eval_bool(member['days'], days)
    if rate:
        condition_bool = condition_bool and eval_bool(member['rate'], rate)
    if points:
        condition_bool = condition_bool and eval_bool(member['points'], points)
    if not int(checked):
        condition_bool = condition_bool and (not member['checked'])
    if not condition_bool:
        return

    if confirm(u'是否发送警告短信? (y/n) '):
        if retry_shanbay(shanbay.send_mail, True, 'bool',
                         [member['username']],
                         settings.warnning_title,
                         render(member, 'warn_mail.txt')):

            print(u'警告短信已发送')
        else:
            print(u'警告短信发送失败')
        return member


def main():
    # 登录
    username = settings.username or input('Username: ').decode(encoding).strip()
    password = settings.password or getpass()
    shanbay = retry_shanbay(Shanbay, False, 'exception',
                            username, password, settings.team_id,
                            settings.team_url)

    # 判断当前时间
    current_datetime = check_time(shanbay, settings)

    # 获取成员信息
    new_members = []       # 新人
    warnning_members = []  # 警告
    dismiss_members = []   # 踢人
    max_page = retry_shanbay(shanbay.max_page, False, 'exception',
                             shanbay.dismiss_url)
    all_members = get_all_members(shanbay, max_page)

    # 设置加入条件
    limit = settings.limit

    if confirm(u'设置小组成员加入条件为：打卡天数>={0} (y/n) '.format(limit)):
        if retry_shanbay(shanbay.update_limit, False, 'bool', limit):
            print(u'设置更新成功')
        else:
            print(u'设置更新失败')
    print('')

    # 对所有成员进行操作
    print(u'开始对所有成员进行处理')
    for member in all_members:
        if member['username'].lower() == username.lower():
            continue
        output_member_info(member)

        # 新人
        if check_welcome(shanbay, member, settings):
            new_members.append(member)

        # 恭喜
        check_congratulate(shanbay, member, settings)

        # 踢人
        if check_dismiss(shanbay, member, settings):
            dismiss_members.append(member)
            continue

        # 警告
        warnning_members.append(member)

    if not settings.confirm:
        # print(u'新人:')
        # for x in new_members:
        #     print(x)
        # print(u'警告:')
        # for x in warnning_members:
        #     print(x)
        print(u'被踢:')
        for x in dismiss_members:
            print(x)

    if confirm(u'更新查卡贴 (y/n)'):
        context = {
            'today': current_datetime.strftime('%Y-%m-%d'),
            'number': len(dismiss_members)
        }
        if not settings.confirm:
            print(context)
        content = render(context, 'dismiss_topic.txt')
        if retry_shanbay(shanbay.reply_topic, False, 'bool',
                         settings.dismiss_topic_id, content):
            print(u'帖子更新成功')
        else:
            print(u'帖子更新失败')

    if confirm(u'更新小组数据贴 (y/n) '):
        context = retry_shanbay(shanbay.team_info, False, 'exception')
        if not settings.confirm:
            print(context)
        content = render(context, 'grow_up_topic.txt')
        if retry_shanbay(shanbay.reply_topic, False, 'bool',
                         settings.grow_up_topic_id, content):
            print(u'帖子更新成功')
        else:
            print(u'帖子更新失败')

    if settings.confirm and confirm(u'设置小组成员加入条件为：打卡天数>=%s (y/n) '
                                    % settings.default_limit):
        if retry_shanbay(shanbay.update_limit, False, 'bool',
                         settings.default_limit):
            print(u'设置更新成功')
        else:
            print(u'设置更新失败')

if __name__ == '__main__':
    print(u'版本：%s' % __version__)
    while True:
        try:
            main()
        except SystemExit:
            pass
        except LoginException:
            print(u'登录失败')
        except:
            print(u'程序运行中出现错误了')
            logger.exception('')
        if confirm(u'退出? (y/n) '):
            break

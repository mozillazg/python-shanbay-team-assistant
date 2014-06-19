#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

"""扇贝网小组管理助手"""

from getpass import getpass
import logging
import sys
import time

from argparse import ArgumentParser
from shanbay import Shanbay, AuthException, Team, Message

from . import __version__
from .conf import Setting
from .utils import eval_bool, render, Retry, PrintStrWriter, _confirm, input

encoding = sys.stdin.encoding
logger = logging.getLogger(__name__)


class Assistant(object):
    def __init__(self, settings, sleep_time=1):
        self.settings = settings
        self.sleep_time = sleep_time
        self.username = settings.username
        self.shanbay = Retry()(Shanbay, self.username, settings.password)
        Retry()(self.shanbay.login)
        self.team = Team(self.shanbay, settings.team_url)
        self.message = Message(self.shanbay)
        self.send_message = self.message.send_message

    def confirm(self, msg):
        """提示信息"""
        return _confirm(self.settings.confirm, msg, self.sleep_time)

    def output_member_info(self, member):
        """输出组员信息"""
        print('用户名: {username:<10} 昵称: {nickname:<20} 组龄: {days:<5}'
              ' 贡献值成长值：{points:<8}'.format(**member)
              + ' 打卡率: {rate}%'.format(**member).ljust(15)
              + ' 昨天是否打卡: '
              + ('是' if member['checked_yesterday'] else '否')
              + '    今天是否打卡：'
              + ('是' if member['checked'] else '否')
              )

    def update_limit(self, days):
        if self.confirm('\n设置小组成员加入条件为：打卡天数>=%s (y/n) ' % days):
            if Retry()(self.team.update_limit, days):
                print('设置更新成功')
            else:
                print('设置更新失败')

    def check_time(self):
        """检查是否到了可以查卡的时间"""
        retry = Retry()
        # 服务器时间
        self.current_datetime = retry(self.shanbay.server_date)
        current_time = self.current_datetime.time()
        # 查卡时间
        print(u'当前时间：%s\n' % self.current_datetime.strftime('%Y-%m-%d %H:%M'))
        if current_time > self.settings.start_time:
            return self.current_datetime
        else:
            print('时间还早者呢，请 {0} 后再操作!'.format(self.settings.start_time))
            self.update_limit(self.settings.default_limit)

    def get_all_members(self, max_page):
        """获取所有成员信息"""
        all_members = []
        for page in range(1, max_page + 1):
            print('获取第%s页的所有成员' % page)
            members = Retry()(self.team.single_page_members, page)
            all_members.extend(members)
            print('%s人' % len(members))
            time.sleep(self.sleep_time)

        print('total: %s人' % len(all_members))
        self.members = all_members
        return all_members

    def check_welcome(self, member):
        """检查是否是新人"""
        if not self.settings.welcome:
            return

        if eval_bool(member['days'], self.settings.welcome):
            if Retry(ignore_error=True)(self.send_message, [member['username']],
                                        self.settings.welcome_title,
                                        render(member,
                                               self.settings.welcome_template,
                                               self.settings.is_template_string
                                               )):

                print('欢迎短信已发送')
            else:
                print('欢迎短信发送失败')
            return member

    def check_congratulate(self, member):
        """恭喜"""
        if not self.settings.congratulate:
            return

        for n, days in enumerate(self.settings.congratulate):
            if member['days'] == days:
                tmps = self.settings.congratulate_template
                # 不同的天数使用不同的模板
                if self.settings.template_order:
                    tmps = [tmps[n]] if len(tmps) > n else tmps

                if Retry(ignore_error=True)(self.send_message, [member['username']],
                                            self.settings.congratulate_title,
                                            render(member, tmps,
                                                   self.settings.is_template_string
                                                   )):
                    print('恭喜短信已发送')
                else:
                    print('恭喜短信发送失败')
                return member

    def announce(self):
        """给所有组员发送通知短信"""
        if not self.confirm('确定要给所有组员发送通知短信？ (y/n) '):
            return

        for member in self.members:
            msg = render(member, [self.settings.announce_file],
                         self.settings.is_template_string)
            if Retry(ignore_error=True)(self.send_message, [member['username']],
                                        self.settings.announce_title, msg):
                print('成功通知 %s' % member['nickname'])
            else:
                print('通知发送失败!')

    def _check_condition(self, conditions, member):
        condition_bool = False
        # 检查是否满足条件
        for condition in conditions:
            days = condition['days']
            rate = condition['rate']
            checked_today = condition['checked_today']
            points = condition['points']
            checked_yesterday = condition['checked_yesterday']

            bool_ = True
            if days:  # 组龄
                bool_ = bool_ and eval_bool(member['days'], days)
            if rate:  # 打卡率
                bool_ = bool_ and eval_bool(member['rate'], rate)
            if points:  # 贡献值
                bool_ = bool_ and eval_bool(member['points'], points)
            if checked_today is not None and (not checked_today):  # 当天未打卡
                bool_ = bool_ and (not member['checked'])
            if checked_yesterday is not None and (not checked_yesterday):  # 昨天未打卡
                bool_ = bool_ and (not member['checked_yesterday'])

            condition_bool = condition_bool or bool_
            if condition_bool:
                break

        return condition_bool

    def check_dismiss(self, member):
        """踢人"""
        if not self.settings.dismiss:
            return

        condition_bool = self._check_condition(self.settings.dismiss, member)
        if not condition_bool:
            return

        if self.confirm('是否踢人并发送踢人短信? (y/n) '):
            if Retry(ignore_error=True)(self.team.dismiss, member['id']):
                print('已执行踢人操作')
                if Retry(ignore_error=True)(self.send_message, [member['username']],
                                            self.settings.dismiss_title,
                                            render(member, self.settings.dismiss_template,
                                                   self.settings.is_template_string
                                                   )):

                    print('踢人短信已发送')
                else:
                    print('踢人短信发送失败')
                return member
            else:
                print('踢人失败')

    def check_warnning(self, member):
        """警告"""
        if not self.settings.warnning:
            return

        condition_bool = self._check_condition(self.settings.warnning, member)
        if not condition_bool:
            return

        if self.confirm('是否发送警告短信? (y/n) '):
            if Retry(ignore_error=True)(self.send_message, [member['username']],
                                        self.settings.warnning_title,
                                        render(member, self.settings.warnning_template,
                                               self.settings.is_template_string
                                               )):

                print('警告短信已发送')
            else:
                print('警告短信发送失败')
            return member

    def update_topic(self, dismiss_num):
        team_info = Retry(ignore_error=True)(self.team.info)

        if self.settings.update_dismiss_topic and self.confirm('\n更新查卡贴 (y/n) '):
            context = {
                'today': self.current_datetime.strftime('%Y-%m-%d'),
                'number': dismiss_num
            }
            content = render(context, self.settings.dismiss_topic_template,
                             self.settings.is_template_string)
            print(content)
            if Retry(ignore_error=True)(self.team.reply_topic,
                                        self.settings.dismiss_topic_id,
                                        content):
                print('帖子更新成功')
            else:
                print('帖子更新失败')

        if self.settings.update_grow_up_topic and self.confirm('\n更新小组数据贴 (y/n) '):
            context = team_info
            context['today'] = self.current_datetime.strftime('%Y-%m-%d')
            content = render(context, self.settings.grow_up_topic_template,
                             self.settings.is_template_string)
            print(content)
            if Retry(ignore_error=True)(self.team.reply_topic,
                                        self.settings.grow_up_topic_id, content):
                print('帖子更新成功')
            else:
                print('帖子更新失败')

        return team_info

    def handle(self):
        new_members = []       # 新人
        congratulate_members = []
        warnning_members = []  # 警告
        dismiss_members = []   # 踢人

        for member in self.members:
            time.sleep(self.sleep_time)
            self.output_member_info(member)
            # 别把自己给踢人
            if member['username'].lower() == self.username.lower():
                continue

            # 新人
            if self.check_welcome(member):
                new_members.append(member)

            # 恭喜
            if self.check_congratulate(member):
                congratulate_members.append(member)

            # 警告
            if self.check_warnning(member):
                warnning_members.append(member)

            # 踢人
            if self.check_dismiss(member):
                dismiss_members.append(member)
        return {
            'new_members': new_members,
            'congratulate_members': congratulate_members,
            'warnning_members': warnning_members,
            'dismiss_members': dismiss_members
        }


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
    settings.announce_file = args.announce
    settings.announce_title = args.title.decode(encoding)
    return settings


def check(settings):
    assistant = Assistant(settings)
    settings = assistant.settings
    team = assistant.team

    if not settings.announce_file:
        # 判断当前时间
        if not assistant.check_time():
            sys.exit(0)

    # 获取成员信息
    max_page = Retry()(team.max_page)
    assistant.get_all_members(max_page)

    # 给全体组员发短信
    if settings.announce_file:
        assistant.announce()
        sys.exit(0)

    # 设置加入条件
    assistant.update_limit(settings.limit)

    # 对所有成员进行操作
    print('\n开始对所有成员进行处理')
    dismiss_members = assistant.handle()['dismiss_members']

    print('\n被踢:')
    for x in dismiss_members:
        assistant.output_member_info(x)
    print('')

    # 更新查卡贴
    team_info = assistant.update_topic(len(dismiss_members))
    # 更新成员加入条件
    assistant.update_limit(settings.default_limit)

    return {
        'members': assistant.members,
        'assistant': assistant,
        'dismiss_members': dismiss_members,
        'team_info': team_info,
    }


def main():
    format_str = ('%(asctime)s - %(name)s'
                  ' - %(funcName)s - %(lineno)d - %(levelname)s'
                  ' - %(message)s')
    logging.basicConfig(filename='debug.log', level=logging.INFO,
                        format=format_str)
    writer = PrintStrWriter()
    sys.stdout = writer
    sys.stderr = writer

    print('版本：%s\n' % __version__)
    settings = parse_conf()
    # 登录
    settings.username = settings.username or input('Username: ').decode(encoding).strip()
    settings.password = settings.password or getpass()

    while True:
        try:
            check(settings)
        except AuthException:
            print('登录失败')
        except (EOFError, KeyboardInterrupt):
            pass
        except Exception as e:
            print('程序运行中出现错误了: %s' % e)
            logging.exception(e)

        if _confirm(settings.confirm, '\n退出? (y/n) ', 0):
            break
        print('\n')

    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__

if __name__ == '__main__':
    main()

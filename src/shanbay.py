#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
import re

from bs4 import BeautifulSoup
import requests


class LoginException(Exception):
    """登录异常
    """
    pass


class Shanbay(object):
    def __init__(self, username, password, headers=None):
        if headers is None:
            self.headers = {
                'User-Agent': ('Mozilla/5.0 (Windows NT 6.2; rv:24.0) '
                               'Gecko/20100101 Firefox/24.0'),
                'Host': 'www.shanbay.com'
            }
        else:
            self.headers = headers
        self.cookies = None
        self.login(username, password)
        self.kwargs = dict(cookies=self.cookies, headers=self.headers)

    def login(self, username, password, url_login=None):
        """登录扇贝网"""
        if url_login is None:
            url_login = 'http://www.shanbay.com/accounts/login/?next=/review/'
        # 首先访问一次网站，获取 cookies
        r_first_vist = requests.head(url_login, headers=self.headers)
        # 获取 cookies 信息
        self.cookies = r_first_vist.cookies.get_dict()

        # 准备用于登录的信息
        # 获取用于防 csrf 攻击的 cookies
        token = self.cookies.get('csrftoken')
        # 设置 headers
        headers_post = copy.copy(self.headers)
        headers_post.update({
            'Refere': url_login,
            'Content-Type': 'application/x-www-form-urlencoded',
        })
        # post 提交的内容
        data_post = {
            'csrfmiddlewaretoken': token,  # csrf
            'username': username,  # 用户名
            'password': password,  # 密码
            'login': '',
        }

        # 提交登录表单同时提交第一次访问网站时生成的 cookies
        r_login = requests.post(url_login, headers=headers_post,
                                cookies=self.cookies, data=data_post,
                                allow_redirects=False, stream=True)
        if r_login.status_code == requests.codes.found:
            # 更新 cookies
            self.cookies.update(r_login.cookies.get_dict())
        else:
            raise LoginException

    def get_team_url(self):
        url = requests.get('http://www.shanbay.com/team/', **self.kwargs).url
        if url == 'http://www.shanbay.com/team/team/':
            raise Exception(u'你还没有加入任何小组')
        else:
            return url

    def get_url_id(self, url):
        return re.findall(r'(\d+)/?$', url)[0]

    def members(self, team_url=None):
        if team_url is None:
            team_url = self.get_team_url()
        # 小组 id
        team_id = self.get_url_id(team_url)
        # 小组管理 - 成员管理 url
        dismiss_url = 'http://www.shanbay.com/team/show_dismiss/%s/' % team_id
        return self.single_page_members(dismiss_url)

    def single_page_members(self, dismiss_url):
        """解析单个页面"""
        html = requests.get(dismiss_url, **self.kwargs).text
        soup = BeautifulSoup(html)
        members_html = soup.find(id='members')

        def get_tag_string(html, class_, tag='td', n=0):
            """获取单个 tag 的文本数据"""
            return html.find_all(tag, class_=class_)[n].get_text().strip()

        members = []
        # 获取成员信息
        for member_html in members_html.find_all('tr', class_='member'):
            member_url = member_html.find_all('a', class_='nickname'
                                              )[0].attrs['href']
            member = {
                'id': self.get_url_id(member_url),
                'nickname': get_tag_string(member_html, 'nickname', 'a'),
                'role': get_tag_string(member_html, 'role'),
                'points': get_tag_string(member_html, 'points'),
                'days': get_tag_string(member_html, 'days'),
                'rate': get_tag_string(member_html, 'rate'),
                'checked_yesterday': get_tag_string(member_html, 'checked'),
                'checked_today': get_tag_string(member_html, 'checked', n=1)
            }
            members.append(member)
        return members


if __name__ == '__main__':
    username = raw_input('username: ')
    password = raw_input('password: ')
    shanbay = Shanbay(username, password)
    members =  shanbay.members()
    for member in members:
        print u'{id}, {nickname}, {role}, {role}, {points}, {days}, {rate}, '\
              '{checked_yesterday}, {checked_today}'.format(**member)

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import datetime
import re
try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode

from bs4 import BeautifulSoup
import requests


class LoginException(Exception):
    """登录异常
    """
    pass


class Shanbay(object):
    def __init__(self, username, password, team_id=None,
                 team_url=None, headers=None):
        if headers is None:
            self.headers = {
                'User-Agent': ('Mozilla/5.0 (Windows NT 6.2; rv:24.0) '
                               'Gecko/20100101 Firefox/24.0'),
                'Host': 'www.shanbay.com'
            }
        else:
            self.headers = headers
        self.cookies = None
        self.csrftoken = None
        self.team_id = team_id
        self.team_url = team_url
        # 登录
        self.login(username, password)
        self.kwargs = dict(cookies=self.cookies, headers=self.headers)
        self.base_data_post = {'csrfmiddlewaretoken': self.csrftoken}

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
        self.csrftoken = self.cookies.get('csrftoken')
        # post 提交的内容
        data_post = {
            'csrfmiddlewaretoken': self.csrftoken,
            'username': username,  # 用户名
            'password': password,  # 密码
            'login': '',
        }

        # 提交登录表单同时提交第一次访问网站时生成的 cookies
        r_login = requests.post(url_login, headers=self.headers,
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
            raise Exception('你还没有加入任何小组')
        else:
            self.team_url = url
            return url

    def get_url_id(self, url):
        return re.findall(r'/(\d+)/?$', url)[0]

    def get_team_id(self):
        self.team_url = self.get_team_url()
        self.team_id = self.get_url_id(self.team_url)
        return self.team_id

    def members(self, team_id=None):
        """获取小组成员"""
        if self.team_id is None:
            self.get_team_id()
        # 小组管理 - 成员管理 url
        dismiss_url = 'http://www.shanbay.com/team/show_dismiss/%s/'
        self.dismiss_url = dismiss_url % self.team_id

        max_page = self.max_page(self.dismiss_url)
        all_members = []
        for page in range(1, max_page + 1):
            url = '%s?page=%s' % (self.dismiss_url, page)
            all_members.extend(self.single_page_members(url))
        return tuple(all_members)

    def max_page(self, url):
        """最大页数"""
        html = requests.get(url, **self.kwargs).text
        soup = BeautifulSoup(html)
        # 分页所在 div
        pagination = soup.find_all(class_='pagination')[0]
        pages = pagination.find_all('li')
        return int(pages[-2].text) if pages else 1

    def single_page_members(self, dismiss_url):
        """获取单个页面内的小组成员"""
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
            mail_url = member_html.find_all('td', class_='operation'
                                            )[0].find('a').attrs['href']
            username = mail_url.split('/')[-2]

            member = {
                'id': self.get_url_id(member_url),
                'username': username,
                # 昵称
                'nickname': get_tag_string(member_html, 'nickname', 'a'),
                # 身份
                'role': get_tag_string(member_html, 'role'),
                # 贡献成长值
                'points': int(get_tag_string(member_html, 'points')),
                # 组龄
                'days': int(get_tag_string(member_html, 'days')),
                # 打卡率
                'rate': float(get_tag_string(member_html, 'rate'
                                             ).split('%')[0]),
                # 昨天是否打卡
                'checked_yesterday': get_tag_string(member_html, 'checked'
                                                    ) != '未打卡',
                # 今天是否打卡
                'checked': get_tag_string(member_html, 'checked',
                                          n=1) != '未打卡',
            }
            members.append(member)
        return tuple(members)

    def dismiss(self, member_id):
        """踢人"""
        url = 'http://www.shanbay.com/team/dismiss/?'
        url += urlencode({
            'team_id': self.team_id,
            'dismiss_member_ids': member_id
        })
        return requests.get(url, **self.kwargs).ok

    def send_mail(self, recipient_list, subject, message):
        """发短信

        :param recipient_list: 收件人列表
        :param subject: 标题
        :param message: 内容

        """
        url = 'http://www.shanbay.com/17mail/compose/'
        recipient = ','.join(recipient_list)
        data = {
            'recipient': recipient,
            'subject': subject,
            'body': message
        }
        data.update(self.base_data_post)
        response = requests.post(url, data=data, **self.kwargs)
        return response.url == 'http://www.shanbay.com/17mail/inbox/'

    def new_topic(self, title, content, team_id=None):
        """小组发贴"""
        data = {
            'title': title,
            'body': content
        }
        data.update(self.base_data_post)
        if team_id is None:
            if self.team_id is None:
                team_id = self.get_team_id()
            else:
                team_id = self.team_id
        url = 'http://www.shanbay.com/api/v1/forum/thread/team_forum_%s/'
        url = url % team_id
        response = requests.post(url, data=data, **self.kwargs)
        return response.url == self.team_url

    def reply_topic(self, topic_id, content):
        """小组回帖"""
        data = {
            'body': content
        }
        data.update(self.base_data_post)
        url = 'http://www.shanbay.com/api/v1/forum/post/thread/%s' % topic_id
        response = requests.post(url, data=data, **self.kwargs)
        if self.team_url is None:
            self.get_team_url()
        topic_url = 'http://www.shanbay.com/team/thread/%s/%s/'
        topic_url = topic_url % (self.team_url, topic_id)
        return response.url == topic_url

    def server_date(self):
        """获取扇贝网服务器时间（北京时间）"""
        date_str = requests.head('http://www.shanbay.com').headers['date']
        date_utc = datetime.datetime.strptime(date_str,
                                              '%a, %d %b %Y %H:%M:%S GMT')
        # 北京时间 = UTC + 8 hours
        return date_utc + datetime.timedelta(hours=8)

    def update_limit(self, days, kind=2, condition='>='):
        """更新成员加入条件"""
        if self.team_id is None:
            self.get_team_id()
        url = 'http://www.shanbay.com/team/setqualification/%s' % self.team_id
        assert days > 0
        data = {
            'kind': kind,
            'condition': condition,
            'value': days,
            'team': self.team_id
        }
        data.update(self.base_data_post)
        response = requests.post(url, data=data, **self.kwargs)
        return response.url == 'http://www.shanbay.com/invite/?kind=team'

    def team_info(self):
        """小组信息"""
        html = requests.get(self.team_url, **self.kwargs).text
        soup = BeautifulSoup(html)

        team_header = soup.find_all(class_='team-header')[0]
        # 标题
        title = team_header.find_all(class_='title')[0].text.strip()
        # 组长
        leader = team_header.find_all(class_='leader'
                                      )[0].find_all('a')[0].text.strip()
        # 创建时间
        date_str = team_header.find_all(class_='date')[0].text.strip()
        date_created = datetime.datetime.strptime(date_str, '%Y/%m/%d')

        team_stat = soup.find_all(class_='team-stat')[0]
        # 排名
        _str = team_stat.find_all(class_='rank')[0].text.strip()
        rank = int(re.findall(r'\d+$', _str)[0])
        # 成员数
        _str = team_stat.find_all(class_='size')[0].text.strip()
        number, max_number = map(int, re.findall(r'(\d+)/(\d+)$', _str)[0])
        # 打卡率
        _str = team_stat.find_all(class_='rate')[0].text.strip()
        rate = float(re.findall(r'(\d+\.?\d+)%$', _str)[0])
        # 总成长值
        _str = team_stat.find_all(class_='points')[0].text.strip()
        points = int(re.findall(r'\d+$', _str)[0])

        return {
            'title': title,
            'leader': leader,
            'date_created': date_created,
            'rank': rank,
            'number': number,
            'max_number': max_number,
            'rate': rate,
            'points': points
        }

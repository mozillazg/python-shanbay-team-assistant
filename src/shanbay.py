#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import copy


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

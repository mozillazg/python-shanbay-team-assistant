#!/usr/bin/env python
# -*- coding: utf-8 -*-

from cx_Freeze import setup, Executable

options = {
    'build_exe': {
        # 'init_script': 'Console',
        'includes': ['lxml'],
        # 'packages': ['lxml'],
        'icon': 'shanbay.ico',
        'include_files': [
            'settings.ini',
            'welcome_mail.txt',
            'congratulate_mail.txt',
            'warn_mail.txt',
            'dismiss_mail.txt',
            'grow_up_topic.txt',
            'dismiss_topic.txt',
         ],
        'include_msvcr': True,
    }
}

setup(
    name='assistant',
    version='0.1.0',
    description='shanbay.com team assistant',
    options=options,
    executables=[Executable("assistant.py")]
)

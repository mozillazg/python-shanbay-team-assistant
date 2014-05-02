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
            'README.md',
            'LICENSE',
            'settings.ini.example',
            'announce.txt.example',
            'welcome_mail.txt.example',
            'congratulate_mail.txt.example',
            'warn_mail.txt.example',
            'dismiss_mail.txt.example',
            'grow_up_topic.txt.example',
            'dismiss_topic.txt.example',
         ],
        'include_msvcr': True,
    }
}

setup(
    name='shanbay-team-assistant',
    version='0.1.5',
    description='shanbay.com team assistant',
    options=options,
    executables=[Executable("assistant.py")]
)

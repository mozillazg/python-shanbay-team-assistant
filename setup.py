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
            'templates/*.example',
         ],
        'include_msvcr': True,
    }
}

setup(
    name='shanbay-team-assistant',
    version='0.1.6.dev',
    description='shanbay.com team assistant',
    options=options,
    executables=[Executable("assistant.py")]
)

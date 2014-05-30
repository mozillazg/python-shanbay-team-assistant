#!/usr/bin/env python
# -*- coding: utf-8 -*-

from glob import glob

from cx_Freeze import setup, Executable

import assistant

options = {
    'build_exe': {
        'packages': ['lxml', 'bs4', 'requests', 'html5lib', 'argparse', 'shanbay'],
        'icon': 'shanbay.ico',
        'include_files': [
            'README.md',
            'LICENSE',
            'CHANGELOG.md',
            'settings.ini.example',
         ] + glob('templates/*.example') + glob('templates/*/*.example'),
        'include_msvcr': True,
    }
}

setup(
    name='shanbay-team-assistant',
    version=assistant.__version__,
    description='shanbay.com team assistant',
    options=options,
    executables=[Executable("assistant.py")]
)

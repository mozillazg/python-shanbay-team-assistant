#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup
import py2exe

options = {
    'py2exe': {
        'optimize': 2,
        'compressed': 1,
        # 'bundle_files': 1,
        'includes': ['lxml', 'html5lib'],
        # 'packages': ['lxml', 'html5lib']
    }
}

setup(console=['assistant.py'], options=options)

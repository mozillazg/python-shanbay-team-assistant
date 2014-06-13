#!/usr/bin/env python
# -*- coding: utf-8 -*-

from glob import glob
from io import open
import os
import re
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

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

try:
    from cx_Freeze import setup, Executable
    kwargs = dict(
        options=options,
        executables=[Executable('assistant.py')],
    )
except ImportError:
    kwargs = {}

current_dir = os.path.dirname(os.path.realpath(__file__))
requirements = [
    'argparse',
    'shanbay==0.2.0',
]
packages = [
    'shanbay_assistant',
]


def read_f(name):
    with open(os.path.join(current_dir, name), encoding='utf8') as f:
        return f.read()


def long_description():
    return read_f('README.md') + '\n\n' + read_f('CHANGELOG.md')


def meta_info(meta, filename='shanbay_assistant/__init__.py', default=''):
    meta = re.escape(meta)
    m = re.search(r"""%s\s+=\s+(?P<quote>['"])(?P<meta>.+?)(?P=quote)""" % meta,
                  read_f(filename))
    return m.group('meta') if m else default


setup(
    name=meta_info('__title__'),
    version=meta_info('__version__'),
    description='shanbay.com team assistant',
    long_description=long_description(),
    url='https://github.com/mozillazg/python-shanbay-team-assistant',
    download_url='',
    author=meta_info('__author__'),
    author_email=meta_info('__email__'),
    license=meta_info('__license__'),
    packages=packages,
    package_data={'': ['LICENSE', 'settings.ini.example',
                       'templates/*.example',
                       'templates/*/*.example',
                       ]
                  },
    package_dir={'shanbay_assistant': 'shanbay_assistant'},
    include_package_data=True,
    install_requires=requirements,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'shanbay_assistant = shanbay_assistant.assistant:main',
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        # 'Programming Language :: Python :: 3',
        # 'Programming Language :: Python :: 3.3',
        # 'Programming Language :: Python :: 3.4',
        'Environment :: Console',
        'Topic :: Utilities',
        'Topic :: Terminals',
    ],
    keywords='shanbay, 扇贝网',
    **kwargs
)

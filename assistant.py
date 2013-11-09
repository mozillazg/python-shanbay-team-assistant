#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
from src import run

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('debug.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(filename)s '
                              '- %(funcName)s - %(lineno)d - %(levelname)s -'
                              ' %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)


def main():
    try:
        run.main()
    except:
        logger.exception('')

if __name__ == '__main__':
    main()
    raw_input(u'退出 > ')

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from src import run

logging.basicConfig(filename='debug.log', level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(filename)s '
                    '- %(funcName)s - %(lineno)d - %(levelname)s -'
                    ' %(message)s')


def main():
    try:
        run.main()
    except SystemExit:
        pass
    except:
        logging.exception('')

if __name__ == '__main__':
    main()
    raw_input(u'退出 > ')

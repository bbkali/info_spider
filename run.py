#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-01-14 13:13:49
# @Word    : python can change world!
# @Version : python3.6

from util.BaiduTb import tbgo
from util.Dj import djgo
from util.Ty import tygo
from threading import Thread
import os
import sys
sys.path.append('scripts')
from scripts.filterfunctions import filterdata
from scripts.exporthtml import goreport

ys = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'result')
config_file = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'conf', 'config.ini')

# 将config_sample.ini 改名为config.ini
if not os.path.exists(config_file):
    os.rename(
        config_file.replace('config.ini', 'config_sample.ini'), config_file)

# 创建result目录
if not os.path.exists(ys):
    os.system("mkdir %s" % ys)

if __name__ == '__main__':
    threads = []
    threads.append(Thread(target=tygo))
    threads.append(Thread(target=tbgo))
    threads.append(Thread(target=djgo))
    for t in threads:
        t.start()
        t.join()
    print('爬取完毕，正在导出结果')
    goreport()

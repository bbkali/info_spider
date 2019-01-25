#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Word    : python can change world!
# @Version : python3.6

from jinja2 import Environment
from jinja2 import FileSystemLoader
from filterfunctions import filterdata
import json
import time
import os
import sys


Base_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'result')


def read_file(all_data, path, type):
    """
    读取json文件，进行过滤，并返回过滤后的字典
    :param path: result下json路径
    :param type: 三种类型中的一种
    :return all_data: 过滤后的内容
    """
    filename = os.path.join(path, str(type) + '.json')
    all_data[type] = filterdata(filename, type).run()
    return all_data


def exporthtml(all_data):
    """
    将所有处理的数据导入result.html中
    :param all_data: 过滤后的内容
    """
    env = Environment(loader=FileSystemLoader(
        os.path.dirname(os.path.abspath(__file__))))
    tpl = env.get_template('templates.html')

    with open(os.path.join(Base_dir, 'result.html'), 'w+', encoding='utf-8') as fout:
        render_content = tpl.render(
            times=time.strftime("%Y%m%d", time.localtime()),
            tbnn=all_data['tb'],
            djnn=all_data['dj'],
            tynn=all_data['ty'],
            count={
                'tb': len(all_data['tb']),
                'dj': len(all_data['dj']),
                'ty': len(all_data['ty'])
            })
        fout.write(render_content)


def goreport():
    """
    主程序：1.遍历result目录下的json文件 2.读取json文件 3.过滤json文件 4.导入生成result.html
    """
    all_data = {'tb': {}, 'dj': {}, 'ty': {}}
    for i in (fns for fns in os.listdir(Base_dir) if fns.endswith(('.json'))):
        read_file(all_data, Base_dir, i.split('.')[0])
    exporthtml(all_data)

# goreport()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Word    : python can change world!
# @Version : python3.6

from configobj import ConfigObj
import os


class Config(object):

    def __init__(self, avg, section):
        """
        :param avg: 属性名称
        :param section: 属于文件中的第几个section，这是整形
        """
        self.section = section
        self.avg = avg
        # 读取文件的内容
        self.path = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), 'config.ini')
        self.cf = ConfigObj(self.path, encoding='UTF8')
        self.data = {
            1: 'Mysql_config',
            2: 'Tb_module_config',
            3: 'Filter_config',
            4: 'Dj_module_config',
            5: 'Ty_module_config'
        }

    def getconfig(self):
        """
        获得想要属性的内容
        :param avg: 属性名称
        :return: 属性的值
        """
        parameter = self.cf[self.data[self.section]][self.avg]
        return parameter

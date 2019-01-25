#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Word    : python can change world!
# @Version : python3.6

import json
import os
import sys
import time
sys.path.append('../')
from conf.config import Config


class filterdata(object):
    """
    这是一个过滤的类
    input: filename（目前只有3种json类型文件）,type（目前只有3种类型）
    return: datas(带中标关键字，以及原始数据处理)
    """

    def __init__(self, filename, type):
        self.filename = filename
        self.type = type
        self.count_type = {'tb': '百度贴吧', 'dj': '大江论坛', 'ty': '天涯论坛'}
        self.num = 0
        self.data = {}
        self.times_off = int(Config('Times_off', 3).getconfig())
        self.glwords = Config('Words_list', 3).getconfig()
        self.expendwords = int(Config('Words_expend_num', 3).getconfig())
        self.md_list_len = int(Config('Md_list_len', 3).getconfig())
        self.Djviewtimeslen = int(Config('Dj_viewtimes_len', 4).getconfig())
        self.Tyviewtimeslen = int(Config('Ty_viewtimes_len', 5).getconfig())
        self.Tbviewtimeslen = int(Config('Tb_viewtimes_len', 2).getconfig())

    def keys_pd(self, inputword):
        """
        过滤关键字
        :param inputword:需要过滤的字符串
       ：return keys：命中的关键字列表
        """
        keys = []
        for i in self.glwords:
            if i in inputword:
                keys.append(i)
        return keys

    def filter_strlen(self, datac, columns, lens):
        """
        规范数据长短（一般针对时间字段）
        :param datac:需要过滤的字典,columns:要过滤的字段,lens:需要截取的长度
        :return datac:已经过滤好的字典 
        """
        datac[columns] = datac[columns][:int(lens)]
        return datac

    def filter_lendatas(self, datac, columns):
        """
        规范数据长短及表达（一般针对list名单缩写）
        :param datac:需要过滤的字典，columns:要过滤的字段
        :return datac:已经过滤好的字典
        """
        if len(datac[columns]) > self.md_list_len:
            datac[columns] = '|'.join(
                datac[columns][:self.md_list_len]) + '->等%s人' % len(datac[columns])
        else:
            datac[columns] = '|'.join(
                datac[columns]) + '->共%s人' % len(datac[columns])
        return datac

    def filter_words(self, datac, columns):
        """
        筛选中标内容,对关键字标红，无关键字标记
        :param datac:需要过滤的字典，columns:要过滤的字段
        :return datac:已经过滤好的字典
        """
        keys = []
        num = 1
        for i in self.glwords:
            if i in datac[columns]:
                if num == 1:
                    start_num = int(datac[columns].find(i)) - self.expendwords
                    end_num = int(datac[columns].find(i)) + self.expendwords
                    if start_num <= 0:
                        start_num = 0
                    cox2 = datac[columns][start_num:end_num].replace(
                        i, '<font color="#FF0000">' + str(i) + '</font>')
                    num += 1
                else:
                    cox2 = cox2.replace(
                        i, '<font color="#FF0000">' + str(i) + '</font>')
                keys.append(i)
        if keys == []:
            if columns == 'word':
                datac[columns] = '内容无中标关键字'
            if columns == 'title':
                datac[columns] = datac[columns]
        else:
            datac[columns] = cox2

        return datac

    def filter_times(self, datac, columns):
        """
        比较现在时间和爬取时间是否一致,主要针对贴吧
        :param datac:需要过滤的字典，columns:要过滤的字段
        :return datac:已经过滤好的字典
        """
        nowtimes = time.strftime("%Y%m%d", time.localtime())
        if nowtimes == datac[columns][:self.Tbviewtimeslen]:
            return 'nice'

    def read_json(self, filename):
        """
        过滤主程序
        :param filename:需要过滤的json资源文件，分tb、ty、dj等分类型处理
        :return datac:已经过滤好的字典
        """
        f = open(filename, 'r', encoding='utf-8')
        for i in list(set(f.readlines())):
            try:
                ss = json.loads(i)
                code = self.keys_pd(ss['word'])
                code1 = self.keys_pd(ss['title'])
                if self.times_off == 1:
                    if self.type == 'tb':
                        if self.filter_times(ss, 'time') == 'nice':
                            pass
                        else:
                            code = ''
                            code1 = ''
                    elif self.type == 'dj':
                        pass
                    elif self.type == 'ty':
                        pass

                if len(code) > 0 or len(code1) > 0:
                    self.num = self.num + 1
                    if len(code) > 0:
                        ss['keyword'] = '|'.join(code)
                    if len(code1) > 0:
                        ss['keyword'] = '|'.join(code1)
                    if self.type == 'tb':
                        ss = self.filter_lendatas(ss, 'cz')
                        ss = self.filter_strlen(
                            ss, 'time', self.Tbviewtimeslen)
                    elif self.type == 'dj':
                        ss = self.filter_strlen(
                            ss, 'create_time', self.Djviewtimeslen)
                        ss = self.filter_strlen(
                            ss, 'reply_time', self.Djviewtimeslen)
                    elif self.type == 'ty':
                        ss = self.filter_strlen(
                            ss, 'create_time', self.Tyviewtimeslen)
                    ss = self.filter_words(ss, 'word')
                    ss = self.filter_words(ss, 'title')
                    self.data[self.num] = ss

            except Exception as e:
                print('读取文件出错', e)

        return self.data

    def run(self):
        """
        运行入口程序
        """
        result = self.read_json(self.filename)
        print(self.count_type[self.type], '筛选出', len(result))
        return result


def test(name):
    """
    测试函数，以ty.json为例,筛选过滤
    """
    Base_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'result')
    path = os.path.join(Base_dir, str(name)+'.json')
    data3 = filterdata(path, str(name)).run()




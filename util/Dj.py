#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Word    : python can change world!
# @Version : python3.6

import requests
import re
import threading
import time
import os
import json
import sys
sys.path.append("../")
from scripts.agents import get_agents
from conf.config import Config
from bs4 import BeautifulSoup
from queue import Queue
from time import strptime
q = Queue()

tmps = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tmp')
f = open(
    tmps.replace('tmp', 'dj.json').replace('util', 'result'),
    'w',
    encoding='utf-8')


class Dj_spider(object):
    """
    这是一个大江论坛爬虫的类,此类为给定一个论坛模块地址就爬取相应信息并保存为dj.json文件
    input: url:论坛模块的地址
    return: 整个模块的符合条件的帖子内容
    """
    header = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Connection': 'keep-alive',
        'Host': 'bbs.jxnews.com.cn',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': get_agents()["User-Agent"]
    }

    def __init__(self, url):
        self.url = url  # 论坛模块地址
        self.data = {}
        self.q = {}  # 存储编号和url
        self.filename = f
        self.sleep_time = int(Config('Dj_next_time', 4).getconfig())
        self.code = Config('Dj_replytimes_off', 4).getconfig()

    def time_check(self, num):
        """
        将小于10的数字转化成带'0'的字符串
        :param num: 属性名称
        """
        if int(num) < 10:
            return '0' + str(num)
        else:
            return str(num)

    def times_change(self, times):
        """
        将现有时间格式化
        :param times: 当前时间
        """
        t2 = strptime(times, "%Y-%m-%d %H:%M")
        tz = str(self.time_check(t2[0])) + str(self.time_check(t2[1])) + str(
            self.time_check(t2[2])) + str(self.time_check(t2[3])) + str(
                self.time_check(t2[4]))
        return tz

    def get_url_list(self, url):
        """
        爬取论坛模块的各个帖子的帖子链接
        :param url: 论坛模块地址
        :return data:{num:url} #num=50
        """
        res = requests.get(self.url, headers=Dj_spider.header)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'lxml')
            data = soup.find_all('tbody')
            num = 1
            for i in data:
                try:
                    title = i.find_all('a', attrs={'class': 's xst'})[0].text
                    url = 'http://bbs.jxnews.com.cn/' + \
                        str(i.find_all('a', attrs={
                            'class': 's xst'})[0]['href'])
                    author = i.find_all('cite')[0].a.text
                    reply_name = i.find_all('cite')[1].a.text
                    create_time = self.times_change(
                        i.find_all('em')[0].span.text)
                    reply_time = self.times_change(i.find_all('em')[2].a.text)
                    self.data[num] = {
                        'title': title,
                        'author': author,
                        'create_time': create_time,
                        'reply_name': reply_name,
                        'reply_time': reply_time,
                        'url': url
                    }
                    self.q[num] = url
                    num += 1
                except Exception as e:
                    print('我是大江,我出现问题了', e)
        else:
            print('爬的有点快，休息一下')

    def get_words(self, url):
        """
        爬取1个帖子的帖子内容
        :param url: 帖子地址
        :return word: 帖子内容
        """
        res = requests.get(url, headers=Dj_spider.header)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'lxml')
            final_data = soup.find_all('font')
            num = 1
            words = []
            for i in final_data:
                try:
                    words.append(
                        i.text.replace('\n', '').replace('\\u', '').replace(
                            ' ', '').replace('\r', ''))
                except Exception as e:
                    pass
            word = '||'.join(list(set(words)))
        else:
            word = ''
            print('[-]访问失败', url)
        return word

    def save_json(self, datatt):
        """
        保存为json格式的资源文件
        :param datatt: 字典格式的数据
        """
        self.filename.write(json.dumps(datatt, ensure_ascii=False) + '\n')

    def run(self):
        """
        类运行程序
        """
        self.get_url_list(self.url)
        for i in range(len(self.data)):
            try:
                # 可以设置时间过滤
                if self.code == '1':
                    if self.data[i + 1]['reply_time'][:8] == time.strftime(
                            "%Y%m%d", time.localtime()):
                        self.data[i + 1]['word'] = self.get_words(
                            self.q[i + 1])
                        self.save_json(self.data[i + 1])
                        time.sleep(self.sleep_time)
                    else:
                        # 不符合时间条件的舍弃
                        pass
                else:
                    self.data[i + 1]['word'] = self.get_words(self.q[i + 1])
                    self.save_json(self.data[i + 1])
                    print(self.data[i + 1])
                    time.sleep(self.sleep_time)
            except Exception as e:
                print('this is dj 有问题', e)


def work():
    """
    与Queue结合的get线程工作
    """
    while q.qsize() > 0:
        url = q.get()
        Dj_spider(url).run()


def djgo():
    """
    主程序运行入口
    """
    print('大江爬虫正在爬取中.....')
    url_list = [
        'http://bbs.jxnews.com.cn/forum-258-1.html',
        'http://bbs.jxnews.com.cn/forum-74-1.html',
        'http://bbs.jxnews.com.cn/forum-291-1.html',
        'http://bbs.jxnews.com.cn/forum-732-1.html',
        'http://bbs.jxnews.com.cn/forum-4-1.html',
        'http://bbs.jxnews.com.cn/forum-576-1.html',
        'http://bbs.jxnews.com.cn/forum-733-1.html',
        'http://bbs.jxnews.com.cn/forum-198-1.html',
        'http://bbs.jxnews.com.cn/forum-572-1.html',
        'http://bbs.jxnews.com.cn/forum-133-1.html',
        'http://bbs.jxnews.com.cn/forum-10-1.html'
    ]
    threads = []
    for i in url_list:
        q.put(i)
    for i in range(int(Config('Ty_threads', 5).getconfig())):
        threads.append(threading.Thread(target=work))
    for t in threads:
        t.start()
    t.join()
    print('大江论坛爬取完成！')

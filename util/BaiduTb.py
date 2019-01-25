#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Word    : python can change world!
# @Version : python3.6

import requests
import re
import json
import os
import random
import sys
from threading import Thread
from queue import Queue
from time import strptime
from time import sleep
from bs4 import BeautifulSoup
sys.path.append("../")
from conf.config import Config
from scripts.agents import get_agents

# 此类为给定一个帖子地址就爬取相应信息并保存为tb.json文件
q = Queue()
tmps = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tmp')
f = open(
    tmps.replace('tmp', 'tb.json').replace('util', 'result'),
    'w',
    encoding='utf-8')


class BaiduTb(object):
    """
    这是一个百度贴吧爬虫的类,此类为给定一个帖子地址就爬取相应信息并保存为tb.json文件
    input: url:帖子的地址 data:装帖子内容的字典容器
    """
    headers = {
        'Host': 'tieba.baidu.com',
        'User-Agent': get_agents()["User-Agent"],
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Referer': 'https://tieba.baidu.com/p/2795723171?pn=2'
    }

    def __init__(self, url, data):
        self.url = url  # 帖子地址
        self.web_type = '没有获取到'  # 贴吧名称
        self.urlist = []  # 帖子地址
        self.lz = '没有获取到'  # 楼主名称
        self.cz = '没有获取到'  # 层主名单
        self.page = '没有获取到'  # 帖子页数
        self.time = '没有获取到'  # 发帖时间
        self.title = '没有获取到'  # 帖子名称
        self.word = '没有获取到'  # 帖子的内容
        self.gjz = Config('Words_list', 3).getconfig()  # 过滤的关键字列表
        self.xs = Config('Tb_replay_on', 2).getconfig()  # 是否显示楼层信息
        self.data = data  # 装载爬取的数据
        self.tmp = tmps
        self.dataprint_off = Config(
            'Tb_printtz_off', 2).getconfig()  # 是否开启打印爬取的帖子内容

    def get_info(self, url):
        title = ''
        try:
            res = requests.get(url, params=self.headers, timeout=5)
        except Exception as e:
            print('访问的有点快了，稍后试一试')
            sleep(2)
            res = requests.get(url, params=self.headers, timeout=5)
        soup = BeautifulSoup(res.content, "lxml")
        for i in soup.find_all('h1'):
            title = i.string.replace(' ', '')
        if title != '':
            self.title = title
        else:
            for i in soup.find_all('h3'):
                title = i.string.replace(' ', '')
        self.title = title
        data3 = soup.find_all(
            'li', attrs={'class': 'l_pager pager_theme_5 pb_list_pager'})
        data = soup.find_all('a', attrs={'class': "card_title_fname"})
        for i in data:
            web_type = (i.string.replace(' ', '').replace('\n', ''))
        self.web_type = web_type
        pages = []
        time = []
        for i in re.findall('>(\d)</a>', str(data3[0])):
            try:
                if str.isdigit(i):
                    pages.append(int(i))
            except Exception as e:
                print(e)
                continue
        if pages != []:
            self.page = max(pages)
        else:
            self.page = 1
        # print('页码为',self.page)
        for i in re.findall('(\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2})',
                            str(soup)):
            try:
                time.append(i)
            except Exception as e:
                continue
        if time != []:
            self.time = time[0]
        else:
            self.time = None

    def get_nr(self, url, pagenum):
        lz = []
        lc = 0
        word = '-'
        word_final = ''
        for page in range(1, int(pagenum) + 1):
            url2 = str(url) + '?pn=' + str(page)
            try:
                res = requests.get(url2, params=self.headers, timeout=5)
            except Exception as e:
                print('访问的有点快了，稍后试一试')
                sleep(2)
                res = requests.get(url2, params=self.headers, timeout=5)
            soup = BeautifulSoup(res.content, "lxml")
            # 抓取楼层信息
            data2 = soup.find_all('cc')
            data = soup.find_all(
                'a',
                attrs={
                    'alog-group': 'p_author',
                    'class': "p_author_name j_user_card"
                })  # 抓取层主和楼主
            data3 = soup.find_all(
                'a',
                attrs={
                    'class': "p_author_name j_user_card",
                    'alog-group': 'p_author',
                })
            for i in data2:
                try:
                    lc += 1
                    word = str(i.get_text().replace(' ', '').replace(
                        '\n', '').replace('\r', '').replace('\\', '').replace(
                            '\t', '').replace('\r', ''))
                    if word:
                        f = open('tmp', 'w+', encoding='utf8')
                        f.write(word + '||')
                        f.close()
                    if self.xs == 'true':
                        print(lc, '楼----')
                        print(word + '||', end='')
                except Exception as e:
                    # print(e)
                    word = ''

                    continue
                word_final += str(word).replace('该楼层疑似违规已被系统折叠 隐藏此楼查看此楼',
                                                '') + '||'
            # print(word_final)
            for i in data:
                try:
                    if i.get_text() != None:
                        lz.append(i.get_text())
                except Exception as e:
                    continue
        self.word = word_final

        try:
            if lz != []:
                self.lz = lz[0]
                self.cz = list(set(lz))
            else:
                for i in data3:
                    print('sss', i.get_text())
                    try:
                        if i.string != None:
                            lz.append(i.string)
                    except Exception as e:
                        continue
                self.lz = lz[0]
                self.cz = list(set(lz))
        except Exception as e:
            print('楼主问题', e)

    def time_check(self, num):
        if int(num) < 10:
            return '0' + str(num)
        else:
            return str(num)

    def times_change(self, times):
        t2 = strptime(times, "%Y-%m-%d %H:%M")
        tz = str(self.time_check(t2[0])) + str(self.time_check(t2[1])) + str(
            self.time_check(t2[2])) + str(self.time_check(t2[3])) + str(
                self.time_check(t2[4]))
        # print(tz)
        return tz

    def save_json(self, title, url, lz, time, cz, word, web_type):
        self.data.write(
            json.dumps({
                'title': title,
                'url': url,
                'lz': lz,
                'time': self.times_change(time),
                'cz': cz,
                'word': word,
                'tb': web_type
            },
                ensure_ascii=False) + '\n')

    def run(self):
        # print('[+]start......',self.url)z
        self.get_info(self.url)
        sleep(1)
        self.get_nr(self.url, self.page)
        try:
            if self.dataprint_off == '1':
                print(
                    '[+]帖子的名称为:%s,贴吧名称为:%s,楼主名称为:%s,帖子地址为:%s,层主名单为:%s,页码数为:%s,发帖时间为：%s'
                    % (str(self.title), self.web_type, str(self.lz), self.url,
                       str(self.cz), self.page, self.time))
            else:
                pass
            # print(self.word)
        except UnicodeEncodeError as e:
            # print(e)
            pass

        try:
            # self.save_mysql(self.title,self.url,self.lz,self.time,str(self.cz),self.web_type,str(self.word),self.page)
            self.save_json(self.title, self.url, self.lz, self.time, self.cz,
                           str(self.word), str(self.web_type))
        except Exception as e:
            print('我是百度贴吧，我出问题了', e)
            pass
        if os.path.exists(self.tmp):
            try:
                os.remove(self.tmp)
            except Exception as e:
                pass


def get_title(url, queue):
    try:
        res = requests.get(url, params=BaiduTb.headers, timeout=5)
    except Exception as e:
        print('爬的有点快休息一下下')
        sleep(2)
        res = requests.get(url, params=BaiduTb.headers, timeout=5)
    soup = BeautifulSoup(res.content, "html.parser")
    web_type = soup.title.string
    data2 = soup.find_all(
        'a', attrs={
            'rel': 'noreferrer',
            'class': "j_th_tit "
        })
    for i in data2:
        q.put('https://tieba.baidu.com' + i.attrs['href'])
        # print(i)
    # print('本页有%s个帖子'%len(self.urlist))
    return q.qsize()


def work():
    while q.qsize() > 0:
        url = q.get()
        sleep(random.randint(0, 3))
        list3 = BaiduTb(url, f).run()


def tbgo():
    print('贴吧爬虫正在爬取中.....')
    for i in Config('Tb_name_list', 2).getconfig():
        for page in range(
                int(Config('Tb_start_page', 2).getconfig()) - 1,
                int(Config('Tb_end_page', 2).getconfig())):
            url = 'http://tieba.baidu.com/f?kw=' + \
                str(i) + '&ie=utf-8&pn=' + str(page * 50)
            num = get_title(url, q)  # 获取帖子链接数量
    print('------------------本次需要爬取%s帖子---------------------' % num)
    threads = []
    for link in range(int(Config('Tb_threads', 2).getconfig())):
        threads.append(Thread(target=work))
    for t in threads:
        t.start()
    t.join()
    print('贴吧爬取完成!')

# tbgo()

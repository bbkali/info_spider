#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Link    : http://www.baidu.com/
# @Version : 3.6

from bs4 import BeautifulSoup as bs
from agents import *
import requests
import random
import re
import random
import json


def check_ip(ip, port, types):

    proxy = {}
    proxy[types] = "%s:%s" % (ip, port)
    # print(proxy)
    # check_url="http://myip.easylife.tw/"
    check_url = "http://www.baidu.com"
    try:
        res = requests.get(
            check_url, headers=get_agents(), proxies=proxy, timeout=2)
        if res.status_code == 200:
            print(proxy)
            return proxy
    except Exception as e:
        # print(e)
        pass


def get_ip(url):
    ip_list = []
    header = get_agents()
    use_ip = []
    res = requests.get(url, headers=get_agents()).content
    soup = bs(res, "html.parser")
    datas = soup.find_all('tr', attrs={'class': re.compile('|^odd')})
    f = open('iplist.txt', 'a')
    try:
        for data in datas:
            soup2 = bs(str(data), "html.parser")
            datas2 = soup2.find_all('td')
            ip = str(datas2[1].string)
            # print(ip)
            port = str(datas2[2].string)
            types = str(datas2[5].string)
            # print(ip,port,types.lower())
            proxy = check_ip(ip, port, types.lower())
            if proxy != None:
                f.write(json.dumps(proxy) + '\n')
                ip_list.append(proxy)
        proxys = random.choice(ip_list)
        print('获得代理ip', proxys)
    except Exception as e:
        print(e)
    finally:
        f.close()
    return proxys


def get_choiceip():
    ip_list = []
    f = open('iplist.txt', 'r')
    for i in f.readlines():
        ip_list.append(i)
    proxy = random.choice(ip_list)
    if proxy:
        try:
            res = requests.get(
                "http://www.baidu.com",
                headers=get_agents(),
                proxies=json.loads(proxy),
                timeout=2)
            if res.status_code == 200:
                print('获得代理ip', proxy)
                return proxy
            else:
                print('重新获取代理ip')
                get_choiceip()
        except Exception as e:
            print(e, '重新获取代理ip')
            get_choiceip()
    else:
        print('ip_list为空，请重新采集')


# get_ip()
# for i in range(1,20):
# 	url='http://www.xicidaili.com/nn/'+str(i)
# 	get_ip(url)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Word    : python can change world!
# @Version : python3.6

from time import strptime
from time import localtime
from time import time
import pymysql
import time
import json

# 此为备选的函数,暂未使用


def save_mysql(tztitle, tburl, tblz, tbtime, tbcz, tbname, tzword, tzpage):
    try:
        conn = pymysql.connect(
            host='127.0.0.1',
            port=3306,
            db='db_name',
            user='db_username',
            passwd='db_passwd',
            charset='utf8')
        cur = conn.cursor()
        sql = "insert into bdtb(tztitle,tburl,tblz,tbtime,tbcz,tbname,tzword,tzpage) value(%s,%s,%s,%s,%s,%s,%s,%s)"
        cur.execute(
            sql, (tztitle, tburl, tblz, tbtime, tbcz, tbname, tzword, tzpage))
    except Exception as e:
        # print(e)
        pass
    finally:
        conn.commit()
        cur.close()
        conn.close()


def find_json(word, title, gjz, list2):

    for i in gjz:
        if word.find(i) != -1 or title.find(i) != -1:
            list2.append(dict(title=title, word=word))
    return list2


def read_json(filename, datas):

    f = open(filename, 'r', encoding='utf-8')
    num = 0
    for i in f.readlines():
        try:
            ss = json.loads(i)
            if Config('Words_list', 3).getconfig() in ss['word']:
                num = num + 1
                datas[num] = ss
        except Exception as e:
            print(e)
            pass


def work():
    datas = {}
    for i in (fns for fns in os.listdir(Base_dir) if fns.endswith(('.json'))):
        path = Base_dir + str(i)
        read_json(path, datas)
    return datas

#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
import web
import re
import logging
from nose.tools import assert_equal


def parse_uptime_info(txt):
    try:
        ret = web.storage()
        flag = 'load average:'
        pos = txt.find(flag)
        txt = txt[pos + len(flag):]
        arr = [x.strip() for x in txt.split(',')]

        ret.load_1 = float(arr[0])
        ret.load_5 = float(arr[1])
        ret.load_15 = float(arr[2])
        return ret
    except:
        logging.exception('parse_uptime_info error:%s', txt)
        return web.storage(load_1=-1, load_5=-1, load_15=-1)


def parse_free_info(txt):
    try:
        ret = web.storage()
        lines = txt.splitlines()

        line = filter(lambda x: x.find('Mem:') != -1, lines)[0]
        arr = [x.strip() for x in re.split(r'\W*', line)]
        total = float(arr[1])
        ret.mem_used = round(float(arr[2]) * 100 / total, 2) if total else 0

        line = filter(lambda x: x.find('Swap:') != -1, lines)[0]
        arr = [x.strip() for x in re.split(r'\W*', line)]
        total = float(arr[1])
        ret.swap_used = round(float(arr[2]) * 100 / total, 2) if total else 0

        return ret
    except:
        logging.exception('parse_free_info error:%s', txt)
        return web.storage(mem_used=-1, swap_used=-1)


def parse_df_info(txt):
    try:
        ret = web.storage()
        lines = [x for x in txt.splitlines() if x.find('%') != -1]

        for line in lines[1:]: # 去掉表头
            arr = [x.strip() for x in re.split(r'\s*', line)]
            ret['disk_use:' + arr[-1]] = int(arr[-2].replace('%', ''))

        return ret
    except:
        logging.exception('parse_df_info error:%s', txt)
        return web.storage({"disk_use:/": -1})


def test_parse_uptime_info():
    txt = ' 14:32:07 up 46 days,  3:40, 10 users,  load average: 2.00, 3.01, 4.02'
    info = parse_uptime_info(txt)
    assert_equal(info.load_1, 2.00)
    assert_equal(info.load_5, 3.01)
    assert_equal(info.load_15, 4.02)


def test_parse_free_info():
    txt = '''total       used       free     shared    buffers     cached
Mem:          1002        941         60          0        154        292
-/+ buffers/cache:        495        506
Swap:         2015          0       2015
    '''
    info = parse_free_info(txt)
    assert_equal(info.mem_used, round(float(941) * 100 / float(1002), 2))
    assert_equal(info.swap_used, 0)


def test_parse_df_info():
    txt = '''Filesystem            Size  Used Avail Use% Mounted on
    /dev/mapper/VolGroup00-LogVol00
                           18G   15G  2.4G  86% /
/dev/sda1              99M   26M   68M  28% /boot
tmpfs                 502M     0  502M   0% /dev/shm
/dev/sdb1              30G  738M   28G   3% /dnspod
    '''
    info = parse_df_info(txt)
    assert_equal(info['disk_use:/'], 86)
    assert_equal(info['disk_use:/boot'], 28)
    assert_equal(info['disk_use:/dev/shm'], 0)
    assert_equal(info['disk_use:/dnspod'], 3)


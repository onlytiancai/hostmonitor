#! /usr/bin/env python
# -*- coding: utf-8 -*-

import time
from collections import defaultdict
import web

import info_parser

hosts = set()
collect_datas = {}
max_metric_list = 100

def add_host(host):
    hosts.add(host)


def add_metric_data(host, name, value):
    if host not in collect_datas:
        collect_datas[host] = defaultdict(list)

    storage = collect_datas[host]

    if len(storage[name]) >= max_metric_list:
        storage[name].pop(0)
    metric_value = [int(time.time()), float(value)]
    storage[name].append(metric_value)


def get_lastest_metrics(host):
    storage = collect_datas.get(host, {})
    ret = []
    for name in storage:
        x = storage[name]
        metric_time = x[-1][0] if x else 0
        metric_value = x[-1][1] if x else 0
        metric_time = time.strftime("%H:%M:%S", time.localtime(float(metric_time)))
        ret.append(web.storage(name=name, time=metric_time, value=metric_value))
    return sorted(ret, key=lambda x: x.name)


def process_data(clientip, data):
    add_host(clientip)

    info = info_parser.parse_uptime_info(data.uptime_info)
    for name in info:
        add_metric_data(clientip, name, info[name])

    info = info_parser.parse_df_info(data.df_info)
    for name in info:
        add_metric_data(clientip, name, info[name])

    info = info_parser.parse_free_info(data.free_info)
    for name in info:
        add_metric_data(clientip, name, info[name])


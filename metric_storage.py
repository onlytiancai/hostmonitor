#! /usr/bin/env python
# -*- coding: utf-8 -*-

import time
from collections import defaultdict
import redis
import web

import config 
import info_parser

r = redis.Redis(**config.redis_conn_args)

hosts = defaultdict(set) 
collect_datas = {}
max_metric_list = 10

def add_host(email, mac_addr, hostname, ip):
    hosts[email].add((mac_addr, hostname, ip))


def get_hosts(email):
    return list(hosts[email])


def clear_hosts(email):
    if email in hosts:
        del hosts[email]


def add_metric_data(mac_addr, name, value):
    if mac_addr not in collect_datas:
        collect_datas[mac_addr] = defaultdict(list)

    storage = collect_datas[mac_addr]

    if len(storage[name]) >= max_metric_list:
        storage[name].pop(0)
    metric_value = [int(time.time()), float(value)]
    storage[name].append(metric_value)


def clear_metrics(mac_addr):
    if mac_addr in collect_datas:
        del collect_datas[mac_addr]


def get_lastest_metrics(mac_addr):
    storage = collect_datas.get(mac_addr, {})
    ret = []
    for name in storage:
        x = storage[name]
        metric_time = x[-1][0] if x else 0
        metric_value = x[-1][1] if x else 0
        metric_time = time.strftime("%H:%M:%S", time.localtime(float(metric_time)))
        ret.append(web.storage(name=name, time=metric_time, value=metric_value))
    return sorted(ret, key=lambda x: x.name)


def process_data(clientip, data):
    mac_addr = data.mac_addr
    add_host(data.email, mac_addr, data.hostname, clientip)

    info = info_parser.parse_uptime_info(data.uptime_info)
    for name in info:
        add_metric_data(mac_addr, name, info[name])

    info = info_parser.parse_df_info(data.df_info)
    for name in info:
        add_metric_data(mac_addr, name, info[name])

    info = info_parser.parse_free_info(data.free_info)
    for name in info:
        add_metric_data(mac_addr, name, info[name])

def test_default():
    import mock
    from nose.tools import assert_equal

    info_parser.parse_df_info = mock.Mock(return_value={'disk_use:/': 80})
    info_parser.parse_free_info = mock.Mock(return_value={'mem_use': 70})
    info_parser.parse_uptime_info = mock.Mock(return_value={'load_1': 1})

    clientip = '127.0.0.1'

    clear_hosts('test@test.com')
    clear_metrics('00:00:00:00')

    data = web.storage(mac_addr='00:00:00:00', email='test@test.com',
                       hostname='host1', uptime_info='', df_info='', 
                       free_info='')
    process_data(clientip, data)
    hosts = get_hosts('test@test.com')
    print hosts
    assert_equal(len(hosts), 1)
    host = hosts[0]
    assert_equal(host[0], '00:00:00:00')
    assert_equal(host[1], 'host1')
    assert_equal(host[2], '127.0.0.1')

    metrics = get_lastest_metrics('00:00:00:00')
    print metrics
    assert_equal(len(metrics), 3)
    assert_equal(metrics[0].name, 'disk_use:/')
    assert_equal(metrics[1].name, 'load_1')
    assert_equal(metrics[2].name, 'mem_use')

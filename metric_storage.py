#! /usr/bin/env python
# -*- coding: utf-8 -*-

import time
import redis
import web

import config
import info_parser

r = redis.Redis(**config.redis_conn_args)
prefix = config.key_prefix


def add_host(email, mac_addr, hostname, ip):
    key = '%s.%s' % (prefix, email)
    r.sadd(key, repr((mac_addr, hostname, ip)))


def get_hosts(email):
    key = '%s.%s' % (prefix, email)
    return [eval(x) for x in r.smembers(key)]


def clear_hosts(email):
    key = '%s.%s' % (prefix, email)
    r.delete(key)


def add_metric_data(mac_addr, name, value):
    key = '%s.%s' % (prefix, mac_addr)
    metric_value = [int(time.time()), float(value)]
    r.hset(key, name, repr(metric_value))


def clear_metrics(mac_addr):
    key = '%s.%s' % (prefix, mac_addr)
    r.delete(key)


def get_lastest_metrics(mac_addr):
    key = '%s.%s' % (prefix, mac_addr)
    storage = dict(r.hgetall(key))
    ret = []
    for name in storage:
        x = eval(storage[name])
        metric_time = x[0] if x else 0
        metric_value = x[1] if x else 0
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

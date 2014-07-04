#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

import web

import config
import utils
import metric_storage 

render = web.template.render('templates', base='layout')

class IndexHandler(object):
    def GET(self):
        data = web.input()
        email = data.get('email')
        return render.index(email)


class DashboardHandler(object):
    def GET(self):
        data = web.input(email='onlytiancai@gmail.com')
        email = data.email
        hosts1, hosts2, hosts3 = [], [], []
        hosts = metric_storage.hosts.get(email, [])
        for i, host in enumerate(hosts):
            mac_addr = host[0]
            metrics = metric_storage.get_lastest_metrics(mac_addr)
            if i % 3 == 0:
                willappend = hosts1
            elif i % 3 == 1:
                willappend = hosts2
            else:
                willappend = hosts3
            willappend.append(web.storage(host=host, metrics=metrics))
        return render.dashboard(email, hosts1, hosts2, hosts3)


class CollectHandler(object):
    'curl http://hostmonitor.ihuhao.com/api/collect -d uptime_info=1 -d df_info=1 -d free_info=1'
    def POST(self):
        clientip = utils.get_clientip()
        data = web.input()
        metric_storage.process_data(clientip, data)

        ret = 'ip=%s\n' % clientip
        metrics = metric_storage.get_lastest_metrics(data.mac_addr)
        ret += '\n'.join('%s=%s' % (metric.name, metric.value) for metric in metrics)
        ret += '\nmac_addr=%s\n' % data.mac_addr 
        ret += 'email=%s\n' % data.email
        ret += 'hostname=%s\n' % data.hostname
        ret += '\n'
        ret += 'please visit http://hostmonitor.ihuhao.com/dashboard?email=%s . \n' % data.email
        return ret

urls = ('/', 'IndexHandler',
        '/dashboard', 'DashboardHandler',
        '/api/collect', 'CollectHandler'
        )

app = web.application(urls, globals())
wsgiapp = app.wsgifunc()

if __name__ == '__main__':
    app.run() 

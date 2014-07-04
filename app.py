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
        hosts1, hosts2, hosts3 = [], [], []
        for i, host in enumerate(metric_storage.hosts):
            metrics = metric_storage.get_lastest_metrics(host)
            if i % 3 == 0:
                willappend = hosts1
            elif i % 3 == 1:
                willappend = hosts2
            else:
                willappend = hosts3
            willappend.append(web.storage(host=host, metrics=metrics))
        return render.index(hosts1, hosts2, hosts3)


class CollectHandler(object):
    'curl http://hostmonitor.ihuhao.com/api/collect -d uptime_info=1 -d df_info=1 -d free_info=1'
    def POST(self):
        clientip = utils.get_clientip()
        data = web.input()
        metric_storage.process_data(clientip, data)

        ret = '%s, ' % clientip
        metrics = metric_storage.get_lastest_metrics(clientip)
        ret += ', '.join('%s=%s' % (metric.name, metric.value) for metric in metrics)
        ret += ', mac_addr=%s' % data.mac_addr 
        ret += ', email=%s' % data.email
        return ret

urls = ('/', 'IndexHandler',
        '/api/collect', 'CollectHandler'
        )

app = web.application(urls, globals())
wsgiapp = app.wsgifunc()

if __name__ == '__main__':
    app.run() 

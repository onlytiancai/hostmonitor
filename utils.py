#! /usr/bin/env python
# -*- coding: utf-8 -*-

import web

def get_clientip():
    return web.ctx.env.get('HTTP_X_REAL_IP', web.ctx.ip)

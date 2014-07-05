#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
import logging

redis_conn_args = dict(host='localhost', port=6379, db=0) 

logging.basicConfig(filename=os.path.join(os.getcwd(), 'log.log'), level = logging.DEBUG)

def reload_config():
    try:
        import config_real
        items = [(k, v) for k, v in config_real.__dict__.items()
                 if not k.startswith('__')]
        globals().update(dict(items))
    except ImportError:
        pass

reload_config()

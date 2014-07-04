#! /usr/bin/env python
# -*- coding: utf-8 -*-


def reload_config():
    try:
        import config_real
        items = [(k, v) for k, v in config_real.__dict__.items()
                 if not k.startswith('__')]
        globals().update(dict(items))
    except ImportError:
        pass

reload_config()

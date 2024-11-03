# -*- coding:utf-8 -*-
# 测试数据的运行时间

import time
import os


def time_measure(func):
    def wrap(*args, **kwargs):
        start = time.time()
        ret = func(*args, **kwargs)
        time_elapsed = time.time() - start
        name = os.path.abspath(func.__name__)
        #print('{0} elapsed {1:.4f} s'.format(name, float(time_elapsed)))
        # -- save model -- #
        # try:
        #     history = json_load('history.json')
        # except:
        #     history = dict()
        #
        # history.setdefault(name, []).append(time_elapsed)
        # json_write('history.json', history)
        return ret

    return wrap
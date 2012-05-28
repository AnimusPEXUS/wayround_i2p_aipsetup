# -*- coding: utf-8 -*-

import os
import copy

def env_vars_edit(var_list, mode='copy'):

    ret = []

    if mode == 'copy':
        ret = copy.copy(os.environ)
    elif mode == 'clean':
        ret = []
    else:
        raise ValueError

    for i in var_list:
        if var_list[i] == None and i in ret:
            del(ret[i])
        else:
            ret[i] = var_list[i]

    return ret

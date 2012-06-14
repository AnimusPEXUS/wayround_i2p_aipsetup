# -*- coding: utf-8 -*-

import traceback

def return_exception_info(e):
    txt = """
-e- EXCEPTION: %(type)s
        VALUE: %(val)s
    TRACEBACK:
%(tb)s
%(feo)s
""" % {
        'type': repr(e[0]),
        'val' : repr(e[1]),
        'tb'  : ''.join(traceback.format_list(traceback.extract_tb(e[2]))),
        'feo' : ''.join(traceback.format_exception_only(e[0], e[1]))
        }

    return txt


def print_exception_info(e):
    txt = return_exception_info(e)
    print(txt)
    return

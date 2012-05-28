# -*- coding: utf-8 -*-

import datetime

def currenttime_stamp():
    d = datetime.datetime.now()
    return time_stamp(d)

def time_stamp(dt):
    return '%(year).4d%(month).2d%(day).2d.%(hour).2d%(minute).2d%(second).2d.%(micro).7d' % {
        'year'  : dt.year,
        'month' : dt.month,
        'day'   : dt.day,
        'hour'  : dt.hour,
        'minute': dt.minute,
        'second': dt.second,
        'micro' : dt.microsecond
        }


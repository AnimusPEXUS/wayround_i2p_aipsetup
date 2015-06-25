#!/usr/bin/python3

import glob
import os.path

SLASH_MARCH = '{}multiarch'.format(os.path.sep)
SLASH_USR = '{}usr'.format(os.path.sep)
PRIM = '{ops}_primary{ops}'.format(ops=os.path.sep)
CROSSBUILDERS = 'crossbuilders'
SBIN = 'sbin'
BIN = 'bin'


# get archs roots bins

archs_roots_bins = \
    glob.glob(os.path.join(SLASH_MARCH, '*', SBIN)) + \
    glob.glob(os.path.join(SLASH_MARCH, '*', BIN))

archs_roots_bins.sort()


# get current_system crossbuilders bins

current_crossbuilders_bins = \
    glob.glob(os.path.join(SLASH_USR, CROSSBUILDERS, '*', SBIN)) + \
    glob.glob(os.path.join(SLASH_USR, CROSSBUILDERS, '*', BIN))

current_crossbuilders_bins.sort()


all_crossbuilders_bins = \
    glob.glob(os.path.join(SLASH_MARCH, '*', CROSSBUILDERS, '*', SBIN)) + \
    glob.glob(os.path.join(SLASH_MARCH, '*', CROSSBUILDERS, '*', BIN))

all_crossbuilders_bins.sort()

lst = current_crossbuilders_bins + archs_roots_bins + all_crossbuilders_bins

for i in range(len(lst) - 1, -1, -1):
    if PRIM in lst[i]:
        del lst[i]

out_line = ':'.join(lst)


if len(out_line) != 0:
    out_line = ':{}'.format(out_line)

print(out_line, end='')

exit(0)

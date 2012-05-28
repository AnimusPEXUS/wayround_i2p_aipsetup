# -*- coding: utf-8 -*-

import threading

def cat(stdin, stdout, threaded=False, write_method_name='write'):
    return dd(stdin, stdout, bs=(2*1024**2), count=None,
              threaded=threaded)

def dd(stdin, stdout, bs=1, count=None, threaded=False, write_method_name='write'):

    if not write_method_name in ['write', 'update']:
        raise ValueError

    if threaded:
        return threading.Thread(
            target=dd,
            args=(stdin, stdout),
            kwargs=dict(bs=bs,
                        count=count,
                        threaded=False,
                        write_method_name=write_method_name)
            )

    else:

        buff = ' '

        c = 0

        while True:
            buff = stdin.read(bs)

            if  len(buff) == 0:
                break

            exec(
                "stdout.%(write_method_name)s(buff)" % {
                    'write_method_name': write_method_name
                    }
                )

            c += 1

            if c == count:
                break

        return

    # control shuld never reach this return
    return

def lbl_write(stdin, stdout, threaded=False):

    if threaded:
        return threading.Thread(
            target=lbl_write,
            args=(stdin, stdout),
            kwargs=dict(threaded=False))
    else:

        while True:
            l = stdin.readline()
            if l == '':
                break
            else:
                l = l.rstrip(' \0\n')

                stdout.write(l)

        return

    return

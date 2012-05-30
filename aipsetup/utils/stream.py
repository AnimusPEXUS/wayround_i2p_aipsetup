# -*- coding: utf-8 -*-

import threading

def cat(stdin, stdout, threaded=False, write_method_name='write',
        close_output_on_eof=False):
    return dd(stdin, stdout, bs=(2*1024**2), count=None,
              threaded=threaded, write_method_name=write_method_name,
              close_output_on_eof=close_output_on_eof)

def dd(stdin, stdout, bs=1, count=None, threaded=False,
       write_method_name='write', close_output_on_eof=False):

    if not write_method_name in ['write', 'update']:
        raise ValueError

    if threaded:
        return threading.Thread(
            target=dd,
            args=(stdin, stdout),
            kwargs=dict(
                bs=bs,
                count=count,
                threaded=False,
                close_output_on_eof=close_output_on_eof,
                write_method_name=write_method_name
                )
            )

    else:

        buff = ' '

        c = 0

        while True:
            buff = stdin.read(bs)

            exec(
                "stdout.%(write_method_name)s(buff)" % {
                    'write_method_name': write_method_name
                    }
                )

            if  len(buff) == 0:
                break

            if count != None:
                c += 1

                if c == count:
                    break

        if close_output_on_eof:
            stdout.close()

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

# -*- coding: utf-8 -*-

import os
# TODO: migrate to multiprocessing
import multiprocessing
import threading
import subprocess

import aipsetup.utils.error


def cat(stdin, stdout, threaded=False, write_method_name='write',
        close_output_on_eof=False, thread_name='Thread'):
    return dd(stdin, stdout, bs=(2*1024**2), count=None,
              threaded=threaded, write_method_name=write_method_name,
              close_output_on_eof=close_output_on_eof,
              thread_name=thread_name)

def dd(stdin, stdout, bs=1, count=None, threaded=False,
       write_method_name='write', close_output_on_eof=False,
       thread_name='Thread'):

    if not write_method_name in ['write', 'update']:
        raise ValueError

    if not hasattr(stdin, 'read'):
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
                write_method_name=write_method_name,
                thread_name=thread_name
                )
            )

    else:

        if thread_name != 'Thread':
            print "-i- Starting `%(name)s' thread" % {
                'name':thread_name
                }

        buff = ' '

        c = 0
        bytes = 0

        if hasattr(stdin, 'seek'):
            try:
                stdin.seek(0)
            except:
                pass

        while True:
            buff = stdin.read(bs)

            exec(
                "stdout.%(write_method_name)s(buff)" % {
                    'write_method_name': write_method_name
                    }
                )

            buff_len = len(buff)
            if buff_len  == 0:
                break
            else:
                bytes += buff_len

            c += 1

            if count != None:
                if c == count:
                    break

        if hasattr(stdout, 'seek'):
            try:
                stdout.seek(0, os.SEEK_END)
            except:
                pass

        if close_output_on_eof:
            if thread_name != 'Thread':
                print "-i-  Closing `%(name)s' thread stdout" % {
                    'name':thread_name
                    }
            stdout.close()

        if thread_name != 'Thread':
            print "-i-   Ending `%(name)s' thread" % {
                'name':thread_name
                }
            print "        {"
            print "           %(num)d cycles worked," % {
                'num' : c                }
            print "           %(size)d bytes (%(sizem)s MiB) transferred," % {
                'size': bytes,
                'sizem': (float(bytes) / 1024 / 1024)
                }
            print "           with buffer size %(bufs)s bytes (%(bufm)s MiB)" % {
                'bufs': bs,
                'bufm': (float(bs) / 1024 / 1024)
                }
            print "        }"
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

def unix_cat(stdin=subprocess.PIPE,
             stdout=subprocess.PIPE,
             stderr=subprocess.PIPE,
             options=[], bufsize=0, cwd=None):

    p = None

    try:
        p = subprocess.Popen(
            ['cat'] + options,
            stdin=stdin, stdout=stdout, stderr=stderr,
            bufsize=bufsize,
            cwd=cwd
            )
    except:
        print "-e- Error starting cat subprocess"
        p = None
        e = sys.exc_info()
        aipsetup.utils.error.print_exception_info(e)
        raise e[1]

    return p


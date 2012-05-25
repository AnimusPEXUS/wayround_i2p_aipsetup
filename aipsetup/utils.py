#!/usr/bin/python
# -*- coding: utf-8 -*-

import ConfigParser
import fcntl
import glob
import os
import os.path
import re
import shutil
import struct
import sys
import traceback
import termios
import subprocess
import copy
import hashlib
import threading
import datetime
import StringIO

import aipsetup.buildingsite


def show_version_message():
    print """\
aipsetup %(version)s

Copyright (C) 2008-2012 Alexey V. Gorshkov (aka AnimusPEXUS)
This is free software; see the source for copying conditions.  There is NO
warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
""" % {
        'version': '3.0'
        }
    return

default_config = {
    'aipsetup_dir': '/mnt/sda3/home/agu/p/aipsetup/aipsetup-3',

    'editor'             : 'emacs',

    'uhtroot'            : '/mnt/sda3/home/agu/_UHT',

    'constitution'       : '/mnt/sda3/home/agu/_UHT/system_constitution.py',

    'builders'           : '/mnt/sda3/home/agu/_UHT/pkg_builders',
    'buildinfo'          : '/mnt/sda3/home/agu/_UHT/pkg_buildinfo',
    'repository'         : '/mnt/sda3/home/agu/_UHT/pkg_repository',
    'source'             : '/mnt/sda3/home/agu/_UHT/pkg_source',
    'info'               : '/mnt/sda3/home/agu/_UHT/pkg_info',

    'repository_index'   : '/mnt/sda3/home/agu/_UHT/index_repository.lst',
    'source_index'       : '/mnt/sda3/home/agu/_UHT/index_source.lst',

    'sqlalchemy_engine_string': 'sqlite:////mnt/sda3/home/agu/_UHT/pkgindex.sqlite',

    'server_ip'          : '127.0.0.1',
    'server_port'        : '8005',
    'server_prefix'      : '/',
    'server_password'    : '123456789',

    'client_local_proto'       : 'http',
    'client_local_host'        : '127.0.0.1',
    'client_local_port'        : '8005',
    'client_local_prefix'      : '/',

    'client_remote_proto'      : 'http',
    'client_remote_host'       : '127.0.0.1',
    'client_remote_port'       : '8005',
    'client_remote_prefix'     : '/'
    }

actual_config = None


def load_config():
    global actual_config

    ret = None

    if actual_config != None:
        ret = actual_config

    else:

        if os.path.isfile('/etc/aipsetup.conf'):
            r = get_configuration(
                default_config,
                '/etc/aipsetup.conf')

            if isinstance(r, dict):
                ret = r
            else:
                ret = None

        actual_config = ret

    return ret


def get_configuration(defaults, file='/etc/aipsetup.conf'):

    ret = defaults

    cp = ConfigParser.RawConfigParser()

    f = None

    try:
        f = open(file, 'r')
    except:
        print "-e- Can't open %(file)s" % {'file': file}
        ret = None

    try:
        cp.readfp(f)
    except:
        print "-e- Can't read %(file)s" % {'file': file}
        ret = None

    f.close()

    if isinstance(ret, dict):

        if cp.has_section('main'):

            for i in defaults:

                if cp.has_option('main', i):

                    ret[i] = cp.get('main', i)

    del(cp)
    return ret


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
    print txt
    return


def remove_if_exists(file_or_dir):
    if os.path.exists(file_or_dir):
        if os.path.isdir(file_or_dir):
            try:
                shutil.rmtree(file_or_dir)
            except:
                print "-e-       can't remove dir %(dir)s" % {
                    'dir': file_or_dir}
                return 1
        else:
            try:
                os.unlink(file_or_dir)
            except:
                print "-e-       can't remove file %(file)s" % {
                    'file': file_or_dir}
                return 1
    return 0

def cleanup_dir(dirname):
    files = glob.glob(os.path.join(dirname, '*'))
    for i in files:
        remove_if_exists(i)
    return

def list_files(config, mask, what):

    lst = glob.glob('%(path)s/%(mask)s' % {
            'path': config[what],
            'mask': mask
            })

    lst2 = []
    for each in lst:
        if isinstance(each, str):
            lst2.append(each.decode('utf-8'))
        else:
            lst2.append(each)
    lst = lst2
    del(lst2)

    lst.sort()

    semi = ''
    if len(lst) > 0:
        semi = ':'

    print 'found %(n)s file(s)%(s)s' % {
        'n': len(lst),
        's': semi
        }

    bases = []
    for each in lst:
        bases.append(os.path.basename(each))

    columned_list_print(bases, fd=sys.stdout.fileno())

    return

def edit_file(config, filename, what):
    return edit_file_direct(config, '%(path)s/%(file)s' % {
            'path': config[what],
            'file': filename
            })


def edit_file_direct(config, filename):
    p = None
    try:
        p = subprocess.Popen([config['editor'], '%(file)s' % {
                    'file': filename
                    }])
    except:
        print '-e- error starting editor'
        print_exception_info(sys.exc_info())
    else:
        try:
            p.wait()
        except:
            print '-e- error waiting for editor'

        print '-i- editor exited'

    del(p)

def copy_file(config, file1, file2, what):
    folder = config[what]

    f1 = os.path.join(folder, file1)
    f2 = os.path.join(folder, file2)

    if os.path.isfile(f1):
        if os.path.exists(f2):
            print "-e- destination file or dir already exists"
        else:
            print "-i- copying %(f1)s to %(f2)s" % {
                'f1': f1,
                'f2': f2
                }
            try:
                shutil.copy(f1, f2)
            except:
                print "-e- Error copying file"
                print_exception_info(sys.exc_info())
    else:
        print "-e- source file not exists"

def get_terminal_size(fd=1):
    res = None
    io_res = None
    arg = struct.pack('HHHH', 0, 0, 0, 0)

    # print "-e- op:%(op)s fd:%(fd)s arg:%(arg)s" % {
    #     'op': repr(termios.TIOCGWINSZ),
    #     'fd': repr(fd),
    #     'arg': repr(arg)
    #     }
    try:
        io_res = fcntl.ioctl(
            fd,
            termios.TIOCGWINSZ,
            arg
            # '        '
            )
    except:
        # print_exception_info(sys.exc_info())
        res = None
    else:
        try:
            res = struct.unpack('HHHH', io_res)
        except:
            # print_exception_info(sys.exc_info())
            res = None


    if res != None:
        res = {
            'ws_row': res[0],
            'ws_col': res[1],
            'ws_xpixel': res[2],
            'ws_ypixel': res[3]
            }

    return res

def columned_list_print(lst, width=None, columns=None,
                        margin_right=u' │ ', margin_left=u' │ ', spacing=u' │ ',
                        fd=1):
    print return_list_print(lst, width=None, columns=None,
                            margin_right=u' │ ', margin_left=u' │ ',
                            spacing=u' │ ', fd=1)

def return_list_print(lst, width=None, columns=None,
                      margin_right=u' │ ', margin_left=u' │ ', spacing=u' │ ',
                      fd=1):

    if width == None:
        if (isinstance(fd, int) and os.isatty(fd)) \
                or (isinstance(fd, file) and fd.isatty()):

            size = get_terminal_size(fd)
            if size == None:
                width = 80
            else:
                width = size['ws_col']
        else:
            width = 80

    longest = 0
    lst_l = len(lst)
    for i in lst:
        l = len(i)
        if l > longest:
            longest = l


    mrr_l = len(margin_right)
    mrl_l = len(margin_left)
    spc_l = len(spacing)

    int_l = width-mrr_l-mrl_l

    if columns == None:
        columns = (int_l / (longest+spc_l))

    if columns < 1:
        columns = 1


    rows = int(lst_l / columns)

    # print "int_l   == " + str(int_l)
    # print "longest == " + str(longest)
    # print "width   == " + str(width)
    # print "lst_l   == " + str(lst_l)
    # print "columns == " + str(columns)

    ret = ''
    for i in range(0, lst_l, columns):
        # print "i == " + str(i)
        l2 = lst[i:i+columns]

        l3 = []
        for j in l2:
            l3.append(j.ljust(longest))

        while len(l3) != columns:
            l3.append(u''.ljust(longest))

        ret += deunicodify("%(mrl)s%(row)s%(mrr)s" % {
                'mrl': margin_left,
                'mrr': margin_right,
                'row': spacing.join(l3)
                })

    return ret


def codify(list_or_basestring, on_wrong_type='exception',
           ftype='str', ttype='unicode', operation='decode',
           coding='utf-8'):

    ret = None
    if isinstance(list_or_basestring, eval(ftype)):
        ret = eval("list_or_basestring.%(opname)s('%(coding)s', 'strict')" % {
                'opname': operation,
                'coding': coding
                })

    elif isinstance(list_or_basestring, eval(ttype)):
        ret = copy.copy(list_or_basestring)

    elif isinstance(list_or_basestring, list):
        l2 = []
        for i in list_or_basestring:
            l2.append(unicodify(i))
        ret = l2
    else:
        if on_wrong_type == 'exception':
            raise TypeError
        elif on_wrong_type == 'copy':
            ret = copy.copy(list_or_basestring)
        else:
            raise Exception

    return ret

def unicodify(list_or_basestring, on_wrong_type='exception'):

    """
    Convert str or list of strs to unicode or list of unicode

    WARNING: (Python >3 `bin' and Python <3 `str') strings all assumed
    to be in UTF-8. decoding will be based only on UTF-8!!!

    dict convertion is not supported

    if on_wrong_type == 'exception' - exception is raised if wrong
    type given, else if on_wrong_type == 'copy' - wrong data just
    copyed

    """

    return codify(list_or_basestring, on_wrong_type='exception',
                  ftype='str', ttype='unicode', operation='decode')

def deunicodify(list_or_basestring, on_wrong_type='exception'):

    """
    Convert unicode or list of unicodes to str or list of strs

    WARNING: (Python >3 `bin' and Python <3 `str') strings all assumed
    to be in UTF-8. encoding will be based only on UTF-8!!!

    dict convertion is not supported

    if on_wrong_type == 'exception' - exception is raised if wrong
    type given, else if on_wrong_type == 'copy' - wrong data just
    copyed

    """

    return codify(list_or_basestring, on_wrong_type='exception',
                  ftype='unicode', ttype='str', operation='encode')

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

def make_dir_checksums(dirname, output_filename):

    ret = 0

    dirname = os.path.abspath(dirname)

    if not os.path.isdir(dirname):
        print "-e- Not is dir %(name)s" % {
            'name': dirname
            }
        ret = 1

    else:

        try:
            summs_fd = open(output_filename, 'w')
        except:
            print "-e- Error opening output file"
            print_exception_info(sys.exc_info())
            ret = 2
        else:
            ret = make_dir_checksums_fo(dirname, summs_fd)

            summs_fd.close()

    return ret

def make_dir_checksums_fo(dirname, output_fileobj):

    ret = 0

    dirname = os.path.abspath(dirname)

    if not os.path.isdir(dirname):
        print "-e- Not a dir %(name)s" % {
            'name': dirname
            }
        ret = 1

    else:

        dirname_l = len(dirname)

        if not isinstance(output_fileobj, file):
            print "-e- Wrong output file object"
            ret = 2
        else:
            summs_fd = output_fileobj

            for root, dirs, files in os.walk(dirname):
                for f in files:
                    if os.path.isfile(root+'/'+f) and not os.path.islink(root+'/'+f):
                        m = hashlib.sha512()
                        fd = open(root+'/'+f, 'r')
                        m.update(fd.read())
                        fd.close()
                        wfn = ('/' + (root+'/'+f)[1:])[dirname_l:]
                        summs_fd.write(m.hexdigest() + ' *' + wfn  + '\n')

    return ret


def _list_files_recurcive(start_root, start_root_len, root_dir, fd):

    ld = os.listdir(root_dir)

    files = unicodify(
        ld
        )

    files.sort()

    for each in files:
        if each in ['.', '..']:
            continue

        full_path = os.path.abspath(
            os.path.join(
                root_dir,
                each)
            )

        if os.path.isdir(full_path) \
                and not os.path.islink(full_path):
            _list_files_recurcive(start_root, start_root_len, full_path, fd)
        else:

            if not os.path.isdir(full_path):
                fd.write("%(filename)s\n" % {
                        'filename': deunicodify(
                            "%(filename)s" % {
                                'filename': full_path[start_root_len:]
                                })
                        }
                    )
            else:
                # TODO: figureout what to do now
                raise Exception

    return

def list_files_recurcive(dirname, output_filename):

    fd = open(output_filename, 'w')
    absp = os.path.abspath(dirname)
    _list_files_recurcive(absp, len(absp), absp, fd)
    fd.close()


def cat(stdin, stdout, threaded=False):
    return dd(stdin, stdout, bs=(2*1024**2), count=None,
              threaded=threaded)

def dd(stdin, stdout, bs=1, count=None, threaded=False):

    if threaded:
        return threading.Thread(
            target=dd,
            args=(stdin, stdout),
            kwargs=dict(bs=bs, count=count, threaded=False))
    else:

        buff = ' '

        c = 0

        while True:
            buff = stdin.read(bs)

            if  len(buff) == 0:
                break

            stdout.write(buff)

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

class Log:

    def __init__(self, config, building_site, logname):

        ret = 0
        self.code = 0
        self.fileobj = None
        self.logname = logname

        log_dir = aipsetup.buildingsite.getDir_BUILD_LOGS(
            building_site
            )

        if not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir)
            except:
                print "-e- Exception while creating building logs dir"
                aipsetup.utils.print_exception_info(sys.exc_info())
                ret = 1
        else:

            if not os.path.isdir(log_dir) \
                    or os.path.islink(log_dir):
                print "-e- Current file type is not acceptable: %(name)s" % {
                    'name': log_dir
                    }
                ret = 2

        if ret == 0:
            timestamp = currenttime_stamp()
            filename = os.path.abspath(
                os.path.join(
                    log_dir,
                    "%(ts)s-%(name)s.txt" % {
                        'ts': timestamp,
                        'name': logname
                        }
                    )
                )
            try:
                self.fileobj = open(filename, 'w')
            except:
                print "-e- Error opening log file"
                print_exception_info(sys.exc_info())
                ret = 3
            else:
                print "[%(ts)s] =///////= Starting `%(name)s' log =///////=\n" % {
                    'ts': timestamp,
                    'name': self.logname
                    }
                self.fileobj.write(
                    "[%(ts)s] =///////= Starting `%(name)s' log =///////=\n" % {
                        'ts': timestamp,
                        'name': self.logname
                    }
                    )

        if ret != 0:
            raise Exception

        return

    def stop(self):
        if self.fileobj == None:
            raise Exception

        timestamp = currenttime_stamp()
        print "[%(ts)s] =///////= Stopping `%(name)s' log =///////=\n" % {
            'ts': timestamp,
            'name': self.logname
            }
        self.fileobj.write("[%(ts)s] =///////= Stopping `%(name)s' log =///////=\n" % {
                'ts': timestamp,
                'name': self.logname
                })
        self.fileobj.flush()
        self.fileobj.close()
        return

    def write(self, text, echo=True):
        if self.fileobj == None:
            raise Exception

        timestamp = currenttime_stamp()
        if echo:
            print "[%(ts)s] %(text)s" % {
                'ts': timestamp,
                'text': deunicodify(text)
                }
        self.fileobj.write("[%(ts)s] %(text)s\n" % {
                'ts': timestamp,
                'text': deunicodify(text)
                })
        return


    def __del__(self):
        if not self.fileobj.closed:
            try:
                self.stop()
            except:
                pass

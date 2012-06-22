# -*- coding: utf-8 -*-

import os
import sys
import struct
import fcntl
import termios
import shutil
import glob

import aipsetup
import aipsetup.utils.text
import aipsetup.utils.error

def remove_if_exists(file_or_dir):
    if os.path.exists(file_or_dir):
        if os.path.isdir(file_or_dir):
            try:
                shutil.rmtree(file_or_dir)
            except:
                print("-e-       can't remove dir %(dir)s" % {
                    'dir': file_or_dir})
                return 1
        else:
            try:
                os.unlink(file_or_dir)
            except:
                print("-e-       can't remove file %(file)s" % {
                    'file': file_or_dir})
                return 1
    return 0

def create_if_not_exists_dir(file_or_dir):
    ret = 0
    if not os.path.exists(file_or_dir):
        try:
            os.makedirs(file_or_dir)
        except:
            ret = 1
        else:
            ret = 0
    else:
        if os.path.isfile(file_or_dir):
            ret = 2
        elif os.path.islink(file_or_dir):
            ret = 3
        elif not os.path.isdir(file_or_dir):
            ret = 4
        else:
            ret = 0
    return ret

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

    print('found %(n)s file(s)%(s)s' % {
        'n': len(lst),
        's': semi
        })

    bases = []
    for each in lst:
        bases.append(os.path.basename(each))

    aipsetup.utils.text.columned_list_print(bases, fd=sys.stdout.fileno())

    return

def copy_file(config, file1, file2, what):
    folder = config[what]

    f1 = os.path.join(folder, file1)
    f2 = os.path.join(folder, file2)

    if os.path.isfile(f1):
        if os.path.exists(f2):
            print("-e- destination file or dir already exists")
        else:
            print("-i- copying %(f1)s to %(f2)s" % {
                'f1': f1,
                'f2': f2
                })
            try:
                shutil.copy(f1, f2)
            except:
                print("-e- Error copying file")
                aipsetup.utils.error.print_exception_info(sys.exc_info())
    else:
        print("-e- source file not exists")


    return

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


def _list_files_recurcive(start_root, start_root_len, root_dir, fd):

    files = os.listdir(root_dir)

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
                        'filename': "%(filename)s" % {
                            'filename': full_path[start_root_len:]
                            }
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

def progress_write(line_to_write):

    width = 80
    ts = get_terminal_size(sys.stdout.fileno())
    if ts != None:
        width = ts['ws_col']

    line_to_write_l = len(line_to_write)
    line_to_out = "\r%(ltw)s%(spaces)s\r" % {
        'ltw': line_to_write,
        'spaces': aipsetup.utils.text.fill(
            ' ', width - line_to_write_l
            )
        }
    sys.stdout.write(line_to_out)
    sys.stdout.flush()
    return

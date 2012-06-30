
import os
import sys
import subprocess
import io
import copy
import re

import aipsetup.utils.error
import aipsetup.utils.stream

LDD_RESP_RES = {
    'not_found': r'(?P<name>.*) => not found',
    'pointed': r'(?P<name>.*) => (?P<path>.*) \((?P<address>.*)\)',
    'singleton': r'(?P<name>.*) \((?P<address>.*)\)'
    }

def elf_deps(filename, mute=True):

    ret = 0

    filename = os.path.abspath(filename)

    if not os.path.isfile(filename):
        #or os.path.islink(filename):
        if not mute:
            print("-e- Not a file")
        ret = 1
    else:

        str_file = io.StringIO()

        lddproc = ldd(
            options=[filename]
            )

        catproc = aipsetup.utils.stream.cat(
            lddproc.stdout,
            str_file,
            threaded=True
            )
        catproc.start()

        lddproc.wait()

        catproc.join()

        str_file.seek(0)

        deps_txt = str_file.read()

        str_file.close()
        del(str_file)

        if lddproc.returncode == 0:
            dep_lst = parse_ldd_output(deps_txt)
            ret = copy.copy(dep_lst)
        else:
            if not mute:
                print("-e- ldd returned error")
            ret = 2

        del(lddproc)

    return ret

def parse_ldd_output(text):
    ret = 0
    dep_lines = text.splitlines()

    dep_lst = []
    for i in dep_lines:

        i = i.strip(' \t\n')

        dep_tmpl = {
            'type'  : None,
            'values': {
                    'name': None,
                    'address':  None,
                    'path': None
                }
            }

        re_res = None
        for j in LDD_RESP_RES:
            re_res = re.match(LDD_RESP_RES[j], i)
            if re_res != None:
                dep_tmpl['type'] = j
                dep_tmpl['values']['name'] = re_res.group('name')
                if j == 'pointed':
                    dep_tmpl['values']['path'] = re_res.group('path')
                if j in ['pointed', 'singleton']:
                    dep_tmpl['values']['address'] = re_res.group('address')

                dep_lst.append(dep_tmpl)

                break

        if re_res == None:
            print("-e- Couldn't parse line `%(txt)s'" % {
                'txt': i
                })
            raise Exception

    ret = dep_lst

    return ret

def ldd(stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        options=[], bufsize=0, cwd=None):

    p = None

    try:
        p = subprocess.Popen(
            ['ldd'] + options,
            stdin=stdin, stdout=stdout, stderr=stderr,
            bufsize=bufsize,
            cwd=cwd
            )
    except:
        print("-e- Error starting ldd subprocess")
        p = None
        e = sys.exc_info()
        aipsetup.utils.error.print_exception_info(e)
        raise e[1]

    return p

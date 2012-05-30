# -*- coding: utf-8 -*-

import os
import sys
import hashlib
import re

import aipsetup.utils.stream
import aipsetup.utils.error

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
            sums_fd = open(output_filename, 'w')
        except:
            print "-e- Error opening output file"
            aipsetup.utils.error.print_exception_info(sys.exc_info())
            ret = 2
        else:
            ret = make_dir_checksums_fo(dirname, sums_fd)

            sums_fd.close()

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
            sums_fd = output_fileobj

            for root, dirs, files in os.walk(dirname):
                for f in files:
                    if os.path.isfile(root+'/'+f) and not os.path.islink(root+'/'+f):
                        m = hashlib.sha512()
                        fd = open(root+'/'+f, 'r')
                        m.update(fd.read())
                        fd.close()
                        wfn = ('/' + (root+'/'+f)[1:])[dirname_l:]
                        sums_fd.write(
                            "%(digest)s *%(pkg_file_name)s\n" % {
                                'digest': m.hexdigest(),
                                'pkg_file_name':wfn
                                }
                            )
                        del(m)

    return ret


def make_fileobj_checksum(fileobj):
    ret = None
    m = None
    m = hashlib.sha512()
    aipsetup.utils.stream.cat(
        fileobj, m, write_method_name='update'
        )
    ret = m.hexdigest()
    del(m)
    return ret


def parse_checksums_text(text):

    ret = 0

    lines = text.splitlines()

    sums = {}

    for i in lines:
        ist = i.strip(' \n\t\0')
        if ist != '':
            re_res = re.match(r'(.*?) \*(.*)', ist)

            if re_res == None:
                ret = 1
                break
            else:
                sums[re_res.group(2)] = re_res.group(1)

    if ret == 0:
        ret = sums

    return ret

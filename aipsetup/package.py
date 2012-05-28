
"""
This module is part of aipsetup.

It't purpuse is to check, install, uninstall package
"""

import tarfile
import sys

import aipsetup.utils.error
import aipsetup.storage.archive

def check_package(config, asp_name):
    """
    Check package on error
    """
    ret = 0

    try:
        tarf = tarfile.open(asp_name, mode='r')
    except:
        print "-e- Can't open file %(name)s"
        print aipsetup.utils.error.return_exception_info(
            sys.exc_info()
            )
        ret = 1
    else:
        fi = aipsetup.storage.archive.tar_member_get_extract_file(
            './package.sha512'
            )
        if not isinstance(fi,  file):
            print "-e- Can't get checksums from package file"
            ret = 2
        else:
            sums_txt = fi.read()
            fi.close()
            sums = aipsetup.utils.checksum.parse_checksums_text(sums_txt)
            del(sums_txt)
            # TODO: to be done

    return ret

def install(config, asp_name, destdir='/'):

    ret = 0

    try:
        tarf = tarfile.open(asp_name, mode='r')
    except:
        print "-e- Can't open file %(name)s"
        aipsetup.utils.error.print_exception_info(sys.exc_info())
        ret = 1
    else:
        print "-i- Installing package's file list"
        try:
            f = tarf.getmember('./06.LISTS/DESTDIR.lst.xz')
        except:
            pass

        # TODO: to be done

    return ret

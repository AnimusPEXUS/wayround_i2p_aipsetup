
import tarfile
import sys

import aipsetup.utils.error
import aipsetup.storage.archive

def check_package(config, asp_name):
    ret = 0

    try:
        tarf = tarfile.open(asp_name, mode='r')
    except:
        print "-e- Can't open file %(name)s"
        print aipsetup.utils.return_exception_info(sys.exc_info())
        ret = 1
    else:
        f = aipsetup.storage.archive.tar_member_get_extract_file(
            './package.sha512'
            )
        sums_txt = f.read()
        f.close()
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
        aipsetup.utils.print_exception_info(sys.exc_info())
        ret = 1
    else:
        print "-i- Installing package's file list"
        try:
            f = tarf.getmember('./06.LISTS/DESTDIR.lst.xz')
        except:
            pass

        # TODO: to be done

    return ret

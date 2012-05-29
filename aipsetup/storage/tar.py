
import sys
import subprocess

import aipsetup.utils.error


def tar_check():
    pass

def tar_version():
    pass

def tar(stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
       options=[], bufsize=0, cwd=None):

    p = None

    try:
        p = subprocess.Popen(
            ['tar'] + options,
            stdin=stdin, stdout=stdout, stderr=stderr,
            bufsize=bufsize,
            cwd=cwd
            )
    except:
        print "-e- Error starting tar subprocess"
        p = None
        e = sys.exc_info()
        aipsetup.utils.error.print_exception_info(e)
        raise e[1]

    return p

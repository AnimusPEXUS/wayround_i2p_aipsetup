
import os
import os.path
import subprocess
import sys

import aipsetup.xz
import aipsetup.tar

def compress_file_xz(infile, outfile, verbose_xz=False):

    ret = 0

    if not os.path.isfile(infile):
        print "-e- Input file not exists: %(name)s" % {
            'name': infile
            }
        ret = 1
    else:
        fi = open(infile, 'rb')
        fo = open(outfile, 'wb')

        options = []
        stderr = subprocess.PIPE

        if verbose_xz:
            options += ['-v']
            stderr = sys.stderr

        options += ['-9', '-M', str(200*1024**2), '-']

        xzproc = aipsetup.xz.xz(
            stdin = fi,
            stdout = fo,
            options = options,
            bufsize = 2*1024**2,
            stderr = stderr
            )

        xzproc.wait()

        fi.close()
        fo.close()

    return ret
        

def compress_dir_contents_tar_xz(dirname, output_filename,
                                 verbose_tar=False, verbose_xz=False):

    dirname = os.path.abspath(dirname)

    if not os.path.isdir(dirname):
        print "-e- Not a directory: %(dirname)s" % {
            'dirname': dirname
            }
    else:
        outf = open(output_filename, 'wb')

        options = []
        stderr = subprocess.PIPE

        if verbose_xz:
            options += ['-v']
            stderr = sys.stderr

        options += ['-9', '-M', str(200*1024**2), '-']

        xzproc = aipsetup.xz.xz(
            stdout = outf,
            options = options,
            bufsize = 2*1024**2,
            stderr = stderr
            )

        options = []
        stderr = subprocess.PIPE

        if verbose_tar:
            options += ['-v']
            stderr = sys.stderr

        options += ['-c', '.']

        tarproc = aipsetup.tar.tar(
            options = options,
            stdin = None,
            stdout = xzproc.stdin,
            cwd = dirname,
            bufsize=2*1024**2,
            stderr = stderr
            )

        tarproc.wait()

        xzproc.stdin.close()

        xzproc.wait()

        outf.close()

    return

def pack_dir_contents_tar(dirname, output_filename,
                          verbose_tar=False):

    dirname = os.path.abspath(dirname)

    if not os.path.isdir(dirname):
        print "-e- Not a directory: %(dirname)s" % {
            'dirname': dirname
            }
    else:
        outf = open(output_filename, 'wb')

        options = []
        stderr = subprocess.PIPE

        if verbose_tar:
            options += ['-v']
            stderr = sys.stderr

        options += ['-c', '.']

        tarproc = aipsetup.tar.tar(
            options = options,
            stdin = None,
            stdout = xzproc.stdin,
            cwd = dirname,
            bufsize=2*1024**2,
            stderr = stderr
            )

        tarproc.wait()

        outf.close()

    return

# -*- codepage: utf-8 -*-

import os
import os.path
import subprocess
import sys
import tarfile


import aipsetup.utils.error
import aipsetup.storage.xz
import aipsetup.storage.tar


def _extract_zip(file_name, output_dir):
    ret = os.system("unzip -qq '%(file_name)s' -d '%(output_dir)s'" % {
            'file_name': file_name,
            'output_dir': output_dir
            })

    return ret

def _extract_tar_7z(file_name, output_dir):
    ret = os.system("7z x -so '%(file_name)s' | tar --no-same-owner --no-same-permissions -xlRC '%(output_dir)s'" % {
            'file_name': file_name,
            'output_dir': output_dir
            })

    return ret

def _extract_tar_arch(file_name, output_dir, arch):

    arch_params = ''

    if arch == 'gzip' or arch == 'bzip2':
        arch_params = '-d'

    else:
        arch_params = '-dv'

    ret = os.system("cat '%(file_name)s' | %(arch)s %(arch_params)s | tar --no-same-owner --no-same-permissions -xlRvC '%(output_dir)s' " % {
            'file_name': file_name,
            'arch': arch,
            'output_dir': output_dir,
            'arch_params': arch_params
            })

    return ret

def extract(file_name, output_dir):

    ret = None

    if file_name.endswith('.tar.lzma'):
        ret = _extract_tar_arch(file_name, output_dir, 'lzma')

    elif file_name.endswith('.tar.bz2'):
        ret = _extract_tar_arch(file_name, output_dir, 'bzip2')

    elif file_name.endswith('.tar.gz'):
        ret = _extract_tar_arch(file_name, output_dir, 'gzip')

    elif file_name.endswith('.tar.xz'):
        ret = _extract_tar_arch(file_name, output_dir, 'xz')

    elif file_name.endswith('.tar.7z'):
        ret = _extract_tar_7z(file_name, output_dir)

    elif file_name.endswith('.tgz'):
        ret = _extract_tar_arch(file_name, output_dir, 'gzip')

    elif file_name.endswith('.zip'):
        pass

    elif file_name.endswith('.7z'):
        pass

    else:
        print "-e- unsupported extension"

    if ret == None:
        print "-e- Not implemented"
        raise Exception

    return ret


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

        xzproc = aipsetup.storage.xz.xz(
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

        xzproc = aipsetup.storage.xz.xz(
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

        tarproc = aipsetup.storage.tar.tar(
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

        tarproc = aipsetup.storage.tar.tar(
            options = options,
            stdin = None,
            stdout = outf,
            cwd = dirname,
            bufsize=2*1024**2,
            stderr = stderr
            )

        tarproc.wait()

        outf.close()

    return


def tar_get_member(tarf, cont_name):
    ret = None

    try:
        ret = tarf.getmember(cont_name)
    except:
        print "-e- Can't get tar member"
        print aipsetup.utils.error.return_exception_info(sys.exc_info())
        ret = 1

    return ret


def tar_member_extract_file(tarf, member):
    ret = None

    try:
        ret = tarf.extractfile(member)
    except:
        print "-e- Can't get tar member"
        print aipsetup.utils.error.return_exception_info(sys.exc_info())
        ret = 1

    return ret

def tar_member_get_extract_file(tarf, cont_name):

    ret = None

    m = tar_get_member(tarf, cont_name)

    if not isinstance(m, tarfile.TarInfo):
        ret = 1
    else:
        fileobj = tar_member_extract_file(tarf, m)

        if not isinstance(fileobj, file):
            ret = 2
        else:
            ret = fileobj

    return ret

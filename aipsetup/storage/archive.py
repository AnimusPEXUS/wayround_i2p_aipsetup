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

def compress_dir_contents_tar_compressor(dirname, output_filename,
                                         compressor,
                                         verbose_tar=False,
                                         verbose_compressor=False):
    ret = 0
    try:
        fobj = open(output_filename, 'w')
    except:
        print "-e- Error opening file for write"
        aipsetup.utils.error.print_exception_info(sys.exc_info())
        ret = 1
    else:
        ret = compress_dir_contents_tar_compressor_fobj(
            dirname, fobj, compressor,
            verbose_tar, verbose_compressor
            )
        fobj.close()
    return ret


def compress_dir_contents_tar_compressor_fobj(dirname, output_fobj,
                                              compressor,
                                              verbose_tar=False,
                                              verbose_compressor=False):
    ret = 0

    if not compressor in ['xz']:
        print "-e- Wrong decompressor requested"
        raise ValueError

    dirname = os.path.abspath(dirname)

    if not os.path.isdir(dirname):
        print "-e- Not a directory: %(dirname)s" % {
            'dirname': dirname
            }
    else:
        options = []
        stderr = subprocess.PIPE

        if verbose_compressor:
            options += ['-v']
            stderr = sys.stderr

        options += ['-9', '-M', str(200*1024**2), '-']

        comprproc = eval("aipsetup.storage.%(compr)s.%(compr)s" % {
                'compr': compressor
                })(
            stdout = output_fobj,
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
            stdout = comprproc.stdin,
            cwd = dirname,
            bufsize=2*1024**2,
            stderr = stderr
            )

        tarproc.wait()

        comprproc.stdin.close()

        comprproc.wait()

    return ret

def decompress_dir_contents_tar_compressor(input_filename, dirname,
                                           compressor,
                                           verbose_tar=False,
                                           verbose_compressor=False):
    ret = 0
    try:
        fobj = open(input_filename, 'r')
    except:
        print "-e- Error opening file for read"
        aipsetup.utils.error.print_exception_info(sys.exc_info())
        ret = 1
    else:
        ret = decompress_dir_contents_tar_compressor_fobj(
            fobj, dirname, compressor, verbose_tar, verbose_compressor
            )
        fobj.close()
    return ret


def decompress_dir_contents_tar_compressor_fobj(input_fobj, dirname,
                                                compressor,
                                                verbose_tar=False,
                                                verbose_compressor=False):

    ret = 0

    if not compressor in ['xz']:
        print "-e- Wrong decompressor requested"
        raise ValueError

    dirname = os.path.abspath(dirname)

    if not os.path.exists(dirname):
        try:
            os.makedirs(dirname)
        except:
            print "-e- Destination dir not exists and cant's be created"
            ret = 1
        else:
            ret = 0
    else:
        if os.path.isfile(dirname):
            print "-e- Destination exists but is file"
            ret = 2
        elif os.path.islink(dirname):
            print "-e- Destination exists but is link"
            ret = 3
        else:
            ret = 0

    if ret != 0:
        print "-e- Error while checking destination dir: %(dirname)s" % {
            'dirname': dirname
            }
    else:
        # compressor
        options = []
        stderr = subprocess.PIPE

        if verbose_compressor:
            options += ['-v']
            stderr = sys.stderr

        options += ['-d', '-']

        comprproc = eval("aipsetup.storage.%(compr)s.%(compr)s" % {
                'compr': compressor
                })(
            stdin = input_fobj,
            stdout = subprocess.PIPE,
            options = options,
            bufsize = 2*1024**2,
            stderr = stderr
            )

        # tar
        options = []
        stderr = subprocess.PIPE

        if verbose_tar:
            options += ['-v']
            stderr = sys.stderr

        options += ['-x', '.']

        tarproc = aipsetup.storage.tar.tar(
            options = options,
            stdin = comprproc.stdout,
            stdout = subprocess.STDOUT,
            cwd = dirname,
            bufsize=2*1024**2,
            stderr = stderr
            )

        comprproc.wait()

        tarproc.stdin.close()

        tarproc.wait()

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

    member = tar_get_member(tarf, cont_name)

    if not isinstance(member, tarfile.TarInfo):
        ret = 1
    else:
        fileobj = tar_member_extract_file(tarf, member)

        if not isinstance(fileobj, tarfile.ExFileObject):
            ret = 2
        else:
            ret = fileobj

    return ret

def tar_member_get_extract_file_to(tarf, cont_name, output_filename):
    ret = 0
    try:
        fd = open(output_filename, 'w')
    except:
        print "-e- Error creating output file %(name)s" % {
            'name': output_filename
            }
        ret = 1
    else:
        fobj = tar_member_get_extract_file(
            tarf, cont_name
            )
        if not isinstance(fobj, tarfile.ExFileObject):
            print "-e- Error getting %(name)s from tar" % {
                'name': cont_name
                }
            ret = 2
        else:
            aipsetup.utils.stream.cat(fobj, fd)
            fobj.close()

        fd.close()

    return ret

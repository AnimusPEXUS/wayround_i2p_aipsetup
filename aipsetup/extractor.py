import os


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

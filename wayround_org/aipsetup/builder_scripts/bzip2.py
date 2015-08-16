
import glob
import os.path
import shutil
import subprocess
import collections

import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.utils.file

import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):
        thr = {}
        thr['CC'] = 'CC={}-gcc'.format(self.host_strong)
        thr['AR'] = 'AR={}-gcc-ar'.format(self.host_strong)
        thr['RANLIB'] = 'RANLIB={}-gcc-ranlib'.format(self.host_strong)
        ret = {'thr': thr}
        return ret

    def define_actions(self):
        return collections.OrderedDict([
            ('dst_cleanup', self.builder_action_dst_cleanup),
            ('src_cleanup', self.builder_action_src_cleanup),
            ('bld_cleanup', self.builder_action_bld_cleanup),
            ('extract', self.builder_action_extract),
            ('build', self.builder_action_build),
            ('distribute', self.builder_action_distribute),
            ('so', self.builder_action_so),
            ('copy_so', self.builder_action_copy_so),
            ('fix_links', self.builder_action_fix_links),
            ])

    def builder_action_build(self, called_as, log):

        ret = autotools.make_high(
            self.buildingsite,
            log=log,
            options=[],
            arguments=[
                'PREFIX={}'.format(self.host_multiarch_dir),
                'CFLAGS=  -fpic -fPIC -Wall -Winline -O2 -g '
                '-D_FILE_OFFSET_BITS=64',
                'libbz2.a',
                'bzip2',
                'bzip2recover'
                ] + [self.custom_data['thr']['CC']] +
            [self.custom_data['thr']['AR']] +
            [self.custom_data['thr']['RANLIB']],
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )

        return ret

    def builder_action_distribute(self, called_as, log):

        ret = autotools.make_high(
            self.buildingsite,
            log=log,
            options=[],
            arguments=[
                'install',
                'PREFIX={}'.format(self.dst_host_multiarch_dir)
                ],
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )

        return ret

    def builder_action_so(self, called_as, log):

        ret = autotools.make_high(
            self.buildingsite,
            log=log,
            options=[],
            arguments=[
                'CFLAGS= -fpic -fPIC -Wall -Winline -O2 -g '
                '-D_FILE_OFFSET_BITS=64',
                'PREFIX={}'.format(self.dst_host_multiarch_dir)
                ] + [self.custom_data['thr']['CC']] +
            [self.custom_data['thr']['AR']] +
            [self.custom_data['thr']['RANLIB']],
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir,
            make_filename='Makefile-libbz2_so'
            )

        return ret

    def builder_action_copy_so(self, called_as, log):

        ret = 0

        di = wayround_org.utils.path.join(self.dst_host_multiarch_dir, 'lib')

        if self.host_strong.startswith('x86_64'):
            di = wayround_org.utils.path.join(self.dst_host_multiarch_dir, 'lib64')

        os.makedirs(di, exist_ok=True)

        try:
            sos = glob.glob(wayround_org.utils.path.join(self.src_dir, '*.so.*'))

            for i in sos:

                base = os.path.basename(i)

                j = wayround_org.utils.path.join(self.src_dir, base)
                j2 = wayround_org.utils.path.join(di, base)

                if os.path.isfile(j) and not os.path.islink(j):
                    shutil.copy(j, j2)

                elif os.path.isfile(j) and os.path.islink(j):
                    lnk = os.readlink(j)
                    os.symlink(lnk, j2)

                else:
                    raise Exception("Programming error")

        except:
            log.exception("Error")
            ret = 2

        return ret

    def builder_action_fix_links(self, called_as, log):

        ret = 0

        bin_dir = wayround_org.utils.path.join(self.dst_host_multiarch_dir, 'bin')
        files = os.listdir(bin_dir)

        try:
            for i in files:

                ff = wayround_org.utils.path.join(bin_dir, i)

                if os.path.islink(ff):

                    base = os.path.basename(
                        os.readlink(ff)
                        )

                    if os.path.exists(ff):
                        os.unlink(ff)

                    os.symlink(base, ff)

        except:
            log.exception("Error")
            ret = 3
        return ret

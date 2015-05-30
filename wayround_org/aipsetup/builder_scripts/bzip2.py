
import glob
import logging
import os.path
import shutil
import subprocess
import collections

import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.utils.file

import wayround_org.aipsetup.builder_scripts.std

# FIXME: host/build/target fix required


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):
        thr = {}
        if self.is_crossbuild:
            thr['CFLAGS'] = ' -I{}'.format(
                os.path.join(self.target_host_root, 'usr', 'include')
                )
            thr['LDFLAGS'] = '-L{}'.format(
                os.path.join(self.target_host_root, 'usr', 'lib')
                )
        return {
            'thr': thr
            }

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

    def builder_action_build(self, log):

        ret = autotools.make_high(
            self.buildingsite,
            log=log,
            options=[],
            arguments=[
                'PREFIX=/usr',
                'CC={}-gcc'.format(self.host),
                'AR={}-ar'.format(self.host),
                'RANLIB={}-ranlib'.format(self.host),
                'CFLAGS=  -fpic -fPIC -Wall -Winline -O2 -g '
                '-D_FILE_OFFSET_BITS=64 ' +
                self.custom_data['thr']['CFLAGS'],
                'LDFLAGS=' + self.custom_data['thr']['LDFLAGS'],
                'libbz2.a',
                'bzip2',
                'bzip2recover'
                ],
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )

        return ret

    def builder_action_distribute(self, log):

        ret = autotools.make_high(
            self.buildingsite,
            log=log,
            options=[],
            arguments=[
                'install',
                'PREFIX=' + os.path.join(self.dst_dir, 'usr')
                ],
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )

        return ret

    def builder_action_so(self, log):

        ret = autotools.make_high(
            self.buildingsite,
            log=log,
            options=[],
            arguments=[
                'CC={}-gcc'.format(self.host),
                'AR={}-ar'.format(self.host),
                'RANLIB={}-ranlib'.format(self.host),
                'CFLAGS= -fpic -fPIC -Wall -Winline -O2 -g '
                '-D_FILE_OFFSET_BITS=64 ' +
                self.custom_data['thr']['CFLAGS'],
                'LDFLAGS= ' + self.custom_data['thr']['LDFLAGS'],
                ],
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir,
            make_filename='Makefile-libbz2_so'
            )

        return ret

    def builder_action_copy_so(self, log):

        ret = 0

        di = os.path.join(self.dst_dir, 'usr', 'lib')

        os.makedirs(di, exist_ok=True)

        try:
            sos = glob.glob(self.src_dir + '/*.so.*')

            for i in sos:

                base = os.path.basename(i)

                j = os.path.join(self.src_dir, base)
                j2 = os.path.join(di, base)

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

    def builder_action_fix_links(self, log):

        ret = 0

        bin_dir = os.path.join(self.dst_dir, 'usr', 'bin')
        files = os.listdir(bin_dir)

        try:
            for i in files:

                ff = os.path.join(bin_dir, i)

                if os.path.islink(ff):

                    base = os.path.basename(os.readlink(ff))

                    if os.path.exists(ff):
                        os.unlink(ff)

                    os.symlink(base, ff)

        except:
            log.exception("Error")
            ret = 3
        return ret

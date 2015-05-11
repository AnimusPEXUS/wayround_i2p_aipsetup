
import logging
import os.path
import subprocess
import collections
import inspect
import shutil

import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.utils.file

import wayround_org.aipsetup.builder_scripts.std
import wayround_org.aipsetup.builder_scripts.gcc


class Builder(wayround_org.aipsetup.builder_scripts.gcc.Builder):

    def define_actions(self):
        self.separate_build_dir = True
        lst = [('apply_pkg_nameinfo', self.builder_action_edit_package_info)]
        r = super().define_actions()

        for i in r.keys():
            lst.append((i, r[i]))

        return collections.OrderedDict(lst)

    def builder_action_edit_package_info(self):

        ret = 0

        files = os.listdir(self.tar_dir)

        tar = None
        for i in files:
            if i.startswith('gcc'):
                tar = i

        if tar is None:
            ret = 1
        else:
            bs = wayround_org.aipsetup.build.BuildingSiteCtl(self.buildingsite)
            bs.apply_pkg_nameinfo_on_buildingsite(tar)
        return ret

    def builder_action_extract(self):
        ret = autotools.extract_high(
            self.buildingsite,
            'gcc',
            unwrap_dir=True,
            rename_dir=False
            )
        return ret

    def builder_action_configure(self):
        """
        prefix = os.path.join(
            '/', 'usr'
            )
        """
        prefix = os.path.join(
            '/', 'usr', 'lib', 'unicorn_crossbuilders', self.target, 'usr'
            )
        mandir = os.path.join(prefix, 'man')
        sysconfdir = os.path.join(prefix, '..', 'etc')
        localstatedir = os.path.join(prefix, '..', 'var')
        

        """

        prefix = self.package_info['constitution']['paths']['usr']
        mandir = self.package_info['constitution']['paths']['man']
        sysconfdir = self.package_info['constitution']['paths']['config']
        localstatedir = self.package_info['constitution']['paths']['var']
        """

        """
        for i in [
                'AR',
                'AS',
                'DLLTOOL',
                'LD',
                #'LIPO',
                'NM',
                'OBJCOPY',
                'OBJDUMP',
                'RANLIB',
                'READELF',
                'STRIP',
                'WINDRES',
                'WINDMC'
                ]:
            additional_parameters += [
                '{}_FOR_TARGET='.format(i.upper()) +
                wayround_org.utils.path.join(
                    self.dst_dir, 'usr', 'lib',
                    'unicorn_crossbuilders',
                    target, 'bin', target + '-{}'.format(i.lower())
                    )
                ]
        """

        ret = autotools.configure_high(
            self.buildingsite,
            options=[
                # experimental options
                # '--enable-targets=all',
                '--enable-tls',
                '--enable-nls',

                # '--enable-targets='
                # 'i486-pc-linux-gnu,'
                # 'i586-pc-linux-gnu,'
                # 'i686-pc-linux-gnu,'
                # 'i786-pc-linux-gnu,'
                # 'ia64-pc-linux-gnu,'
                # 'x86_64-pc-linux-gnu,'
                # 'aarch64-linux-gnu',

                # then lto enabled it causes problems to systemd.
                # some time has passed since then - trying to enable lto
                # '--disable-lto',

                # normal options
                #'--enable-__cxa_atexit',

                # disabled for experiment
                #'--with-arch-32=i486',
                #'--with-tune=generic',

                '--enable-languages=c,c++,java,objc,obj-c++,ada,fortran',
                #'--enable-languages=c,c++,ada',
                # '--enable-bootstrap',
                '--enable-threads=posix',
                #'--disable-threads',
                '--enable-multiarch',
                #'--disable-multiarch',
                '--enable-multilib',
                #'--disable-multilib',
                #'--enable-checking=release',
                '--with-gmp=/usr',
                '--with-mpfr=/usr',
                # '--with-build-time-tools=
                # /home/agu/_sda3/_UNICORN/b/gnat/
                # gnat-gpl-2014-x86-linux-bin',
                #'--enable-shared',

                '--with-sysroot=' + os.path.normpath(
                    os.path.join(prefix, '..')
                    ),
                #'--without-headers',


                '--prefix=' + prefix,
                '--mandir=' + mandir,
                '--sysconfdir=' + sysconfdir,
                '--localstatedir=' + localstatedir,

                '--host=' + self.host,
                '--build=' + self.build,
                '--target=' + self.target
                ],
            arguments=[],
            environment={
                # 'CC': '/home/agu/_sda3/_UNICORN/b/gnat/
                #  gnat-gpl-2014-x86-linux-bin/bin/gcc',
                # 'CXX': '/home/agu/_sda3/_UNICORN/b/
                # gnat/gnat-gpl-2014-x86-linux-bin/bin/g++',
                },
            environment_mode='copy',
            source_configure_reldir=self.source_configure_reldir,
            use_separate_buildding_dir=self.separate_build_dir,
            script_name='configure',
            run_script_not_bash=False,
            relative_call=False
            )
        return ret

    def builder_action_build(self):
        ret = autotools.make_high(
            self.buildingsite,
            options=['-j2'],
            arguments=['all-gcc'],
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret

    def builder_action_distribute(self):
        ret = autotools.make_high(
            self.buildingsite,
            options=[],
            arguments=[
                'install-gcc',
                'DESTDIR=' + self.dst_dir
                ],
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret

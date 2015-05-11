
import logging
import os.path
import collections

import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools

import wayround_org.aipsetup.builder_scripts.glibc


class Builder(wayround_org.aipsetup.builder_scripts.glibc.Builder):

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
            if i.startswith('glibc'):
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
            'glibc',
            unwrap_dir=True,
            rename_dir=False
            )
        return ret

    def builder_action_configure(self):

        prefix = os.path.join(
            '/', 'usr', 'lib', 'unicorn_crossbuilders', self.target, 'usr'
            )
        mandir = os.path.join(prefix, 'man')
        sysconfdir = os.path.join(prefix, '..', 'etc')
        localstatedir = os.path.join(prefix, '..', 'var')

        headers_path = wayround_org.utils.path.join(
            prefix, 'include'
            )

        ret = autotools.configure_high(
            self.buildingsite,
            options=[
                '--enable-obsolete-rpc',
                '--enable-kernel=3.19',
                '--enable-tls',
                '--with-elf',
                '--enable-multi-arch',

                # this is from configure --help. configure looking for
                # linux/version.h file

                #'--with-headers=/usr/src/linux/include',

                '--with-headers=' + headers_path,

                '--enable-shared',

                '--prefix=' + prefix,
                '--mandir=' + mandir,
                '--sysconfdir=' + sysconfdir,
                '--localstatedir=' + localstatedir,

                '--host=' + self.host,
                '--build=' + self.build,
                '--target=' + self.target
                ],
            arguments=['libc_cv_forced_unwind=yes'],
            environment={},
            environment_mode='copy',
            source_configure_reldir=self.source_configure_reldir,
            use_separate_buildding_dir=self.separate_build_dir,
            script_name='configure',
            run_script_not_bash=False,
            relative_call=False
            )
        return ret

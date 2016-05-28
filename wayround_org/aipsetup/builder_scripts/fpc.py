
import copy
import subprocess
import os.path
import re

import wayround_org.utils.path
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std

import wayround_org.aipsetup.build


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_actions(self):

        ret = super().define_actions()

        for i in ['autogen', 'build']:
            if i in ret:
                del ret[i]

        return ret

    def builder_action_configure(self, called_as, log):

        p = subprocess.Popen(
            [
                'fpcmake',
                '-Tall'  # TODO: make this automatic
                ],
            cwd=wayround_org.aipsetup.build.getDIR_SOURCE(
                self.buildingsite_path
                ),
            stdout=log.stdout,
            stderr=log.stderr
            )

        ret = p.wait()

        return ret

    def builder_action_distribute(self, called_as, log):

        target = self.get_package_info()['constitution']['arch']

        st = wayround_org.utils.system_type.SystemType(target)
        cpu = st.cpu

        # print("cpu: {}".format(cpu))
        linux_headers_arch = None
        if re.match(r'^i[4-6]86$', cpu) or re.match(r'^x86(_32)?$', cpu):
            settings = {
                'CPU_TARGET': 'i386',
                'PREFIX': self.calculate_install_prefix(),
                'INSTALL_PREFIX': self.calculate_dst_install_prefix(),
                'AS': 'as --32',
                'LD': 'ld -A elf_i386',
                'ppc': 'ppc386'
                }
        elif re.match(r'^x86_64$', cpu):
            settings = {
                'CPU_TARGET': 'x86_64',
                'PREFIX': self.calculate_install_prefix(),
                'INSTALL_PREFIX': self.calculate_dst_install_prefix(),
                'AS': 'as --64',
                'LD': 'ld -A elf_x86_64',
                'ppc': 'ppcx64'
                }
        else:
            logging.error("Don't know which ARCH settings to apply")
            ret = 3

        cmd = [
            'make',
            'clean',
            'fpc_info',
            'all',
            'install',
            'CPU_TARGET={}'.format(settings['CPU_TARGET']),
            'PREFIX={}'.format(settings['PREFIX']),
            'INSTALL_PREFIX={}'.format(settings['INSTALL_PREFIX']),
            'AS={}'.format(settings['AS']),
            'LD={}'.format(settings['LD']),
            ]

        tmp_dir = wayround_org.aipsetup.build.getDIR_TEMP(
            self.buildingsite_path
            )

        tmp_bin_dir = os.path.join(
            tmp_dir,
            'bin'
            )

        os.makedirs(tmp_bin_dir, exist_ok=True)

        # NOTE: FreePascal make system is suck, so it not always accounts
        #       for LD= parameter, so creating special scripst is required
        ld_script_filename = os.path.join(
            tmp_bin_dir,
            '{}-linux-ld'.format(settings['CPU_TARGET'])
            )

        with open(ld_script_filename, 'w') as f:
            f.write(
                """\
#!/bin/bash

{} $@
""".format(settings['LD'])
                )
        os.chmod(ld_script_filename, 0o700)

        enver = copy.deepcopy(os.environ)
        enver['PATH'] += ':{}'.format(tmp_bin_dir)

        log.info('    make')
        for i in range(1, len(cmd)):
            log.info('        {}'.format(cmd[i]))

        p = subprocess.Popen(
            cmd,
            cwd=wayround_org.aipsetup.build.getDIR_SOURCE(
                self.buildingsite_path
                ),
            stdout=log.stdout,
            stderr=log.stderr,
            env=enver
            )

        ret = p.wait()

        if ret == 0:

            version = self.get_package_info(
                )['pkg_nameinfo']['groups']['version_dirty']

            os.symlink(
                os.path.join(
                    '..', 'lib', 'fpc', version, settings['ppc']
                    ),
                os.path.join(
                    settings['INSTALL_PREFIX'],
                    'bin',
                    settings['ppc']
                    )
                )

        return ret


import logging
import os.path

import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.buildtools.waf as waf
import wayround_org.utils.file


def main(buildingsite, action=None):

    ret = 0

    r = wayround_org.aipsetup.build.build_script_wrap(
        buildingsite,
        ['extract', 'configure', 'build', 'distribute'],
        action,
        "help"
        )

    if not isinstance(r, tuple):
        logging.error("Error")
        ret = r

    else:

        self.package_info, actions = r

        src_dir = wayround_org.aipsetup.build.getDIR_SOURCE(buildingsite)

        dst_dir = wayround_org.aipsetup.build.getDIR_DESTDIR(buildingsite)

        source_configure_reldir = '.'

        cwd = os.path.join(src_dir, source_configure_reldir)

        if 'extract' in actions:
            if os.path.isdir(src_dir):
                logging.info("cleaningup source dir")
                wayround_org.utils.file.cleanup_dir(src_dir)
            ret = autotools.extract_high(
                buildingsite,
                self.package_info['pkg_info']['basename'],
                unwrap_dir=True,
                rename_dir=False
                )

        if 'configure' in actions and ret == 0:

            log = wayround_org.utils.log.Log(
                wayround_org.aipsetup.build.getDIR_BUILD_LOGS(buildingsite),
                'waf_configure'
                )

            ret = waf.waf(
                cwd,
                options=[
                    '--prefix=' + self.package_info['constitution']['paths']['usr'],
#                    '--mandir=' + self.package_info['constitution']['paths']['man'],
#                    '--sysconfdir=' +
#                        self.package_info['constitution']['paths']['config'],
#                    '--localstatedir=' +
#                        self.package_info['constitution']['paths']['var'],
                    ],
                arguments=['configure'],
                environment={'PYTHON': '/usr/bin/python3'},
                environment_mode='copy',
                log=log
                )

            log.stop()

        if 'build' in actions and ret == 0:
            log = wayround_org.utils.log.Log(
                wayround_org.aipsetup.build.getDIR_BUILD_LOGS(buildingsite),
                'waf_configure'
                )

            ret = waf.waf(
                cwd,
                options=[
                    '--prefix=' + self.package_info['constitution']['paths']['usr'],
#                    '--mandir=' + self.package_info['constitution']['paths']['man'],
#                    '--sysconfdir=' +
#                        self.package_info['constitution']['paths']['config'],
#                    '--localstatedir=' +
#                        self.package_info['constitution']['paths']['var'],
                    ],
                arguments=['build'],
                environment={'PYTHON': '/usr/bin/python3'},
                environment_mode='copy',
                log=log
                )

            log.stop()

        if 'distribute' in actions and ret == 0:
            log = wayround_org.utils.log.Log(
                wayround_org.aipsetup.build.getDIR_BUILD_LOGS(buildingsite),
                'waf_configure'
                )

            ret = waf.waf(
                cwd,
                options=[
                    '--prefix=' + self.package_info['constitution']['paths']['usr'],
#                    '--mandir=' + self.package_info['constitution']['paths']['man'],
#                    '--sysconfdir=' +
#                        self.package_info['constitution']['paths']['config'],
#                    '--localstatedir=' +
#                        self.package_info['constitution']['paths']['var'],
                    '--destdir=' + dst_dir
                    ],
                arguments=[
                    'install'
                    ],
                environment={'PYTHON': '/usr/bin/python3'},
                environment_mode='copy',
                log=log
                )

            log.stop()

    return ret


import logging
import os.path
import subprocess

import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.utils.file


def main(buildingsite, action=None):

    ret = 0

    r = wayround_org.aipsetup.build.build_script_wrap(
        buildingsite,
        ['extract', 'patch', 'autoreconf', 'configure', 'build', 'distribute',
         'post_install_script'
         ],
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

        separate_build_dir = False

        source_configure_reldir = '.'

        makefile_am = os.path.join('doc', 'man', 'Makefile.am')

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

        if 'patch' in actions and ret == 0:

            try:
                f = open(os.path.join(src_dir, makefile_am))

                lines = f.read().splitlines()

                f.close()

                for i in range(len(lines)):

                    if lines[i] == 'man8dir\t  = $(mandir)/man8':
                        lines[i] = 'man_MANS = install-catalog.8'

                    if lines[i] == 'man8_DATA = *.8':
                        lines[i] = ''

                f = open(os.path.join(src_dir, makefile_am), 'w')

                f.write('\n'.join(lines))

                f.close()
            except:
                logging.exception("Error")
                ret = 1

        if 'autoreconf' in actions and ret == 0:
            p = subprocess.Popen(['autoreconf', '-f', '-i'], cwd=src_dir)
            ret = p.wait()

        if 'configure' in actions and ret == 0:
            ret = autotools.configure_high(
                buildingsite,
                options=[
                    '--prefix=' + self.package_info['constitution']['paths']['usr'],
                    '--mandir=' + self.package_info['constitution']['paths']['man'],
                    '--sysconfdir=' +
                        self.package_info['constitution']['paths']['config'],
                    '--localstatedir=' +
                        self.package_info['constitution']['paths']['var'],
                    '--enable-shared',
                    '--host=' + self.package_info['constitution']['host'],
                    '--build=' + self.package_info['constitution']['build'],
#                    '--target=' + self.package_info['constitution']['target']
                    ],
                arguments=[],
                environment={},
                environment_mode='copy',
                source_configure_reldir=source_configure_reldir,
                use_separate_buildding_dir=separate_build_dir,
                script_name='configure',
                run_script_not_bash=False,
                relative_call=False
                )

        if 'build' in actions and ret == 0:
            ret = autotools.make_high(
                buildingsite,
                options=[],
                arguments=[],
                environment={},
                environment_mode='copy',
                use_separate_buildding_dir=separate_build_dir,
                source_configure_reldir=source_configure_reldir
                )

        if 'distribute' in actions and ret == 0:
            ret = autotools.make_high(
                buildingsite,
                options=[],
                arguments=[
                    'install',
                    'DESTDIR=' + dst_dir
                    ],
                environment={},
                environment_mode='copy',
                use_separate_buildding_dir=separate_build_dir,
                source_configure_reldir=source_configure_reldir
                )

        if 'post_install_script' in actions and ret == 0:

            f = open(os.path.join(buildingsite, 'post_install.py'), 'w')

            f.write(
"""\
#!/usr/bin/python3

import subprocess

def main(basedir):

    subprocess.Popen(
        ['install-catalog',
         '--add',
         '/etc/sgml/sgml-ent.cat',
         '/usr/share/sgml/sgml-iso-entities-8879.1986/catalog'
        ]
        ).wait()

    subprocess.Popen(
        ['install-catalog',
         '--add',
         '/etc/sgml/sgml-docbook.cat',
         '/etc/sgml/sgml-ent.cat'
        ]
        ).wait()

"""
                )

            f.close()

    return ret

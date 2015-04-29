
import logging
import os.path
import shutil

import wayround_org.utils.path

import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.utils.file


def main(buildingsite, action=None):

    ret = 0

    r = wayround_org.aipsetup.build.build_script_wrap(
        buildingsite,
        ['extract', 'configure', 'build', 'distribute', 'reallign_dist'],
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

        java_dir = os.path.join(dst_dir, 'usr', 'lib', 'java')

        etc_dir = os.path.join(dst_dir, 'etc', 'profile.d', 'SET')

        java009 = os.path.join(etc_dir, '009.java')

        classpath000 = os.path.join(etc_dir, '000.classpath')

        separate_build_dir = False

        source_configure_reldir = '.'

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
            ret = autotools.configure_high(
                buildingsite,
                options=[
                    # '--with-jobs=1',
                    '--with-zlib=system',
                    '--with-alsa',
                    # '--with-freetype',
                    '--with-x',
                    '--prefix=' + self.package_info['constitution']['paths']['usr'],
                    '--mandir=' + self.package_info['constitution']['paths']['man'],
                    '--sysconfdir=' +
                    self.package_info['constitution']['paths']['config'],
                    '--localstatedir=' +
                    self.package_info['constitution']['paths']['var'],
                    #                    '--enable-shared',
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
                    'INSTALL_PREFIX=' + dst_dir
                    ],
                environment={},
                environment_mode='copy',
                use_separate_buildding_dir=separate_build_dir,
                source_configure_reldir=source_configure_reldir
                )

        if 'reallign_dist' in actions and ret == 0:
            # ret =

            existing_result_dir = None

            resulted_java_dir_basename = None

            files = os.listdir(dst_dir)

            if 'bin' in files:
                shutil.rmtree(wayround_org.utils.path.join(dst_dir, 'bin'))

            if not 'jvm' in files:
                ret = 10

            if ret == 0:
                files = os.listdir(
                    wayround_org.utils.path.join(
                        dst_dir,
                        'jvm'))

                if len(files) != 1:
                    ret = 11
                else:
                    resulted_java_dir_basename = files[0]

            if ret == 0:

                try:
                    os.makedirs(java_dir)

                    os.rename(
                        wayround_org.utils.path.join(
                            dst_dir,
                            'jvm',
                            resulted_java_dir_basename
                            ),
                        wayround_org.utils.path.join(
                            java_dir,
                            resulted_java_dir_basename
                            )
                        )
                except:
                    logging.exception("can't move java dir to new location")
                    ret = 12

            if ret == 0:
                files = os.listdir(dst_dir)

                if 'jvm' in files:
                    shutil.rmtree(wayround_org.utils.path.join(dst_dir, 'jvm'))

            if ret == 0:
                try:
                    for i in [
                            wayround_org.utils.path.join(java_dir, 'jre'),
                            wayround_org.utils.path.join(java_dir, 'jdk'),
                            wayround_org.utils.path.join(java_dir, 'java')
                            ]:

                        if os.path.islink(i):
                            os.unlink(i)

                        os.symlink(resulted_java_dir_basename, i)
                except:
                    logging.exception("can't create symlinks")
                    ret = 13

            if ret == 0:

                os.makedirs(etc_dir, exist_ok=True)

                fi = open(java009, 'w')

                fi.write(
                    """\
#!/bin/bash
export JAVA_HOME=/usr/lib/java/jdk
export PATH=$PATH:$JAVA_HOME/bin:$JAVA_HOME/jre/bin
export MANPATH=$MANPATH:$JAVA_HOME/man
if [ "${#LD_LIBRARY_PATH}" -ne "0" ]; then
    LD_LIBRARY_PATH+=":"
fi
export LD_LIBRARY_PATH+="$JAVA_HOME/jre/lib/i386:$JAVA_HOME/jre/lib/i386/client"
"""
                    )

                fi.close()

                fi = open(classpath000, 'w')
                fi.write(
                    """\
#!/bin/bash
export CLASSPATH='/usr/lib/java/classpath/*'
"""
                    )

    return ret

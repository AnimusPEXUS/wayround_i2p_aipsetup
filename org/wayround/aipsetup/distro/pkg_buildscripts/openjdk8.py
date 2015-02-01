
import logging
import os.path
import shutil

import org.wayround.utils.path

import org.wayround.aipsetup.build
import org.wayround.aipsetup.buildtools.autotools as autotools
import org.wayround.utils.file


def main(buildingsite, action=None):

    ret = 0

    r = org.wayround.aipsetup.build.build_script_wrap(
        buildingsite,
        ['extract', 'configure', 'build', 'distribute', 'reallign_dist'],
        action,
        "help"
        )

    if not isinstance(r, tuple):
        logging.error("Error")
        ret = r

    else:

        pkg_info, actions = r

        src_dir = org.wayround.aipsetup.build.getDIR_SOURCE(buildingsite)

        dst_dir = org.wayround.aipsetup.build.getDIR_DESTDIR(buildingsite)

        java_dir = os.path.join(dst_dir, 'usr', 'lib', 'java')

        etc_dir = os.path.join(dst_dir, 'etc', 'profile.d', 'SET')

        java009 = os.path.join(etc_dir, '009.java')

        classpath000 = os.path.join(etc_dir, '000.classpath')

        separate_build_dir = False

        source_configure_reldir = '.'

        if 'extract' in actions:
            if os.path.isdir(src_dir):
                logging.info("cleaningup source dir")
                org.wayround.utils.file.cleanup_dir(src_dir)
            ret = autotools.extract_high(
                buildingsite,
                pkg_info['pkg_info']['basename'],
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
                    '--prefix=' + pkg_info['constitution']['paths']['usr'],
                    '--mandir=' + pkg_info['constitution']['paths']['man'],
                    '--sysconfdir=' +
                    pkg_info['constitution']['paths']['config'],
                    '--localstatedir=' +
                    pkg_info['constitution']['paths']['var'],
                    #                    '--enable-shared',
                    '--host=' + pkg_info['constitution']['host'],
                    '--build=' + pkg_info['constitution']['build'],
                    #                    '--target=' + pkg_info['constitution']['target']
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
                shutil.rmtree(org.wayround.utils.path.join(dst_dir, 'bin'))

            if not 'jvm' in files:
                ret = 10

            if ret == 0:
                files = os.listdir(
                    org.wayround.utils.path.join(
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
                        org.wayround.utils.path.join(
                            dst_dir,
                            'jvm',
                            resulted_java_dir_basename
                            ),
                        org.wayround.utils.path.join(
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
                    shutil.rmtree(org.wayround.utils.path.join(dst_dir, 'jvm'))

            if ret == 0:
                try:
                    for i in [
                            org.wayround.utils.path.join(java_dir, 'jre'),
                            org.wayround.utils.path.join(java_dir, 'jdk'),
                            org.wayround.utils.path.join(java_dir, 'java')
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

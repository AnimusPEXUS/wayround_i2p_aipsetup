
import copy
import glob
import logging
import os.path
import re
import shutil
import subprocess

import org.wayround.aipsetup.build
import org.wayround.aipsetup.buildtools.autotools as autotools
import org.wayround.utils.file


def main(buildingsite, action=None):

    ret = 0

    r = org.wayround.aipsetup.build.build_script_wrap(
        buildingsite,
        ['extract', 'configure', 'build', 'distribute'],
        action,
        "help"
        )

    if not isinstance(r, tuple):
        logging.error("Error")
        ret = r

    else:

        pkg_info, actions = r

        tar_dir = org.wayround.aipsetup.build.getDIR_TARBALL(buildingsite)

        src_dir = org.wayround.aipsetup.build.getDIR_SOURCE(buildingsite)

        src_jdk_dir = os.path.join(src_dir, 'openjdk.build', 'j2sdk-image')

        java_exec = os.path.join(src_jdk_dir, 'bin', 'java')

        dst_dir = org.wayround.aipsetup.build.getDIR_DESTDIR(buildingsite)

        java_dir = os.path.join(dst_dir, 'usr', 'lib', 'java')

        etc_dir = os.path.join(dst_dir, 'etc', 'profile.d', 'SET')

        java009 = os.path.join(etc_dir, '009.java')

        classpath000 = os.path.join(etc_dir, '000.classpath')

        separate_build_dir = False

        source_configure_reldir = '.'

        envi = copy.copy(os.environ)
        if 'JAVA_HOME' in envi:
            del envi['JAVA_HOME']

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
                    #                    '--disable-tests',
                    #                    '--disable-jdk-tests',
                    #                    '--disable-langtools-tests',
                    #                    '--disable-hotspot-tests',
                    #                    '--disable-bootstrap',
                    #                    '--with-jdk-home=/home/agu/_sda3/_UNICORN/b2/java/jdk1.7.0_55',
                    '--with-jdk-home=/usr/lib/java/jdk',
                    '--prefix=' + pkg_info['constitution']['paths']['usr'],
                    '--mandir=' + pkg_info['constitution']['paths']['man'],
                    '--sysconfdir=' +
                    pkg_info['constitution']['paths']['config'],
                    '--localstatedir=' +
                    pkg_info['constitution']['paths']['var'],
                    '--enable-shared',
                    '--host=' + pkg_info['constitution']['host'],
                    '--build=' + pkg_info['constitution']['build'],
                    #                    '--target=' + pkg_info['constitution']['target']
                    ],
                arguments=[],
                environment=envi,
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
                environment=envi,
                environment_mode='copy',
                use_separate_buildding_dir=separate_build_dir,
                source_configure_reldir=source_configure_reldir
                )

        if 'distribute' in actions and ret == 0:

            ver = ''

            p = subprocess.Popen(
                [java_exec, '-version'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
                )

            comm = p.communicate()

            stdou = comm[0]

            ver_str = str(stdou.splitlines()[0], encoding='utf-8')

            m = re.match('java version "(.*)"', ver_str)
            if not m:
                logging.error("Error getting version")
                ret = 10
            else:
                ver = m.group(1)

            teaname = 'icedtea-' + ver
            print(teaname)

            jdk_dir = os.path.join(java_dir, teaname)

            os.makedirs(java_dir, exist_ok=True)

            org.wayround.utils.file.copytree(
                src_jdk_dir,
                jdk_dir,
                clear_before_copy=True,
                overwrite_files=True,
                dst_must_be_empty=False
                )

            for i in [
                    os.path.join(java_dir, 'jre'),
                    os.path.join(java_dir, 'jdk'),
                    os.path.join(java_dir, 'java')
                    ]:

                if os.path.islink(i):
                    os.unlink(i)

                os.symlink(teaname, i)

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
export LD_LIBRARY_PATH+=\
"$JAVA_HOME/jre/lib/i386:$JAVA_HOME/jre/lib/i386/client"

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

            src_downs = glob.glob(src_dir + os.path.sep + '*.tar*')

            for i in src_downs:
                logging.info("Copying source {}".format(os.path.basename(i)))
                shutil.copyfile(i, tar_dir + os.path.sep + os.path.basename(i))

    return ret


import logging
import os.path
import shutil

import wayround_org.utils.path

import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.utils.file

import logging
import os.path
import collections
import shutil

import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.utils.file

import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):
        return None

    def define_actions(self):
        ret = super().define_actions()

        ret['after_distribute'] = self.builder_action_after_distribute

        return ret

    def builder_action_edit_package_info(self, called_as, log):

        ret = 0

        try:
            name = self.package_info['pkg_info']['name']
        except:
            name = None

        pi = self.package_info

        if self.is_crossbuilder:
            pi['pkg_info']['name'] = 'cb-binutils-{}'.format(self.target)
        else:
            pi['pkg_info']['name'] = 'binutils'

        bs = self.control
        bs.write_package_info(pi)

        return ret

    def builder_action_extract(self, called_as, log):

        ret = super().builder_action_extract(called_as, log)

        if ret == 0:

            for i in ['corba', 'hostspot', 'jaxp', 'jaxws',
                      'langtools', 'nashorn']:

                if autotools.extract_high(
                        self.buildingsite,
                        i,
                        log=log,
                        unwrap_dir=False,
                        rename_dir=i
                        ) != 0:

                    log.error("Can't extract component: {}".format(i))
                    ret = 2

        return ret

    def builder_action_configure_define_options(self, called_as, log):

        ret = super().builder_action_configure_define_options(called_as, log)
        ret += [
            '--with-jobs=1',
            '--with-zlib=system',
            '--with-alsa',
            # '--with-freetype',
            '--with-x',
            '--with-boot-jdk=/home/agu/_local/_LAILALO/b/javaboot/jdk1.8.0_45'
            ]
        if '--enable-shared' in ret:
            ret.remove('--enable-shared')
        return ret

    def builder_action_distribute(self, called_as, log):
        ret = autotools.make_high(
            self.buildingsite,
            log=log,
            options=[],
            arguments=[
                'install',
                'INSTALL_PREFIX=' + self.dst_dir
                ],
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret

    def builder_action_after_distribute(self, called_as, log):
        ret = 0

        java_dir = os.path.join(self.dst_dir, 'usr', 'lib', 'java')

        etc_dir = os.path.join(self.dst_dir, 'etc', 'profile.d', 'SET')

        java009 = os.path.join(etc_dir, '009.java.sh')

        existing_result_dir = None

        resulted_java_dir_basename = None

        files = os.listdir(self.dst_dir)

        if 'bin' in files:
            shutil.rmtree(wayround_org.utils.path.join(self.dst_dir, 'bin'))

        if not 'jvm' in files:
            ret = 10

        if ret == 0:
            files = os.listdir(
                wayround_org.utils.path.join(
                    self.dst_dir,
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
                        self.dst_dir,
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
            files = os.listdir(self.dst_dir)

            if 'jvm' in files:
                shutil.rmtree(
                    wayround_org.utils.path.join(
                        self.dst_dir,
                        'jvm'))

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

        return ret

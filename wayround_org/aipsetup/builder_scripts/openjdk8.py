

import os.path
import collections
import shutil
import logging

import wayround_org.utils.path
import wayround_org.utils.file

import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std

# TODO: more work required


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):
        return None

    def define_actions(self):
        ret = super().define_actions()

        ret['after_distribute'] = self.builder_action_after_distribute

        return ret

    def builder_action_extract(self, called_as, log):

        ret = super().builder_action_extract(called_as, log)

        if ret == 0:

            components_with_problems = []

            for i in [
                    'corba',
                    'hotspot',
                    'jaxp',
                    'jaxws',
                    'langtools',
                    'nashorn',
                    'jdk'
                    ]:

                if autotools.extract_high(
                        self.buildingsite_path,
                        'jdk-' + i,
                        log=log,
                        unwrap_dir=False,
                        rename_dir=i
                        ) != 0:

                    log.error("Can't extract component: {}".format(i))
                    components_with_problems.append(i)
                    ret = 2
                    break

            if len(components_with_problems) != 0:
                for i in components_with_problems:
                    log.error("Can't extract component: {}".format(i))

        return ret

    def builder_action_configure_define_opts(self, called_as, log):

        ret = super().builder_action_configure_define_opts(called_as, log)
        ret += [
            # '--with-jobs=1',
            '--with-zlib=system',
            '--with-alsa',
            # '--with-freetype',
            '--with-x',
            # '--with-boot-jdk=/home/agu/_local/_LAILALO/b/javaboot/jdk1.8.0_45'
            ]
        if '--enable-shared' in ret:
            ret.remove('--enable-shared')

        return ret

    def builder_action_build_define_cpu_count(self, called_as, log):
        return 1  # NOTE: openjdk has problems with this

    def builder_action_distribute(self, called_as, log):
        ret = autotools.make_high(
            self.buildingsite_path,
            log=log,
            options=[],
            arguments=[
                'install',
                'INSTALL_PREFIX={}'.format(self.get_dst_dir())
                ],
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret

    def builder_action_after_distribute(self, called_as, log):
        ret = 0

        java_dir = wayround_org.utils.path.join(
            self.calculate_install_prefix(),
            'opt',
            'java'
            )

        dst_java_dir = wayround_org.utils.path.join(
            self.get_dst_dir(),
            java_dir
            )

        etc_dir = wayround_org.utils.path.join(
            self.get_dst_dir(),
            'etc',
            'profile.d',
            'SET'
            )

        java009 = wayround_org.utils.path.join(
            etc_dir,
            '009.java.{}.{}.sh'.format(
                self.get_host_from_pkgi(),
                self.get_arch_from_pkgi()
                )
            )

        existing_result_dir = None

        resulted_java_dir_basename = None

        files = os.listdir(self.get_dst_dir())

        if 'bin' in files:
            shutil.rmtree(
                wayround_org.utils.path.join(
                    self.get_dst_dir(),
                    'bin'
                    )
                )

        if not 'jvm' in files:
            ret = 10

        if ret == 0:
            files = os.listdir(
                wayround_org.utils.path.join(
                    self.get_dst_dir(),
                    'jvm'
                    )
                )

            if len(files) != 1:
                ret = 11
            else:
                resulted_java_dir_basename = files[0]

        if ret == 0:

            try:
                os.makedirs(dst_java_dir)

                os.rename(
                    wayround_org.utils.path.join(
                        self.get_dst_dir(),
                        'jvm',
                        resulted_java_dir_basename
                        ),
                    wayround_org.utils.path.join(
                        dst_java_dir,
                        resulted_java_dir_basename
                        )
                    )
            except:
                logging.exception("can't move java dir to new location")
                ret = 12

        if ret == 0:
            files = os.listdir(self.get_dst_dir())

            if 'jvm' in files:
                shutil.rmtree(
                    wayround_org.utils.path.join(
                        self.get_dst_dir(),
                        'jvm'
                        )
                    )

        if ret == 0:
            try:
                for i in [
                        wayround_org.utils.path.join(dst_java_dir, 'jre'),
                        wayround_org.utils.path.join(dst_java_dir, 'jdk'),
                        wayround_org.utils.path.join(dst_java_dir, 'java')
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
export JAVA_HOME={java_dir}/jdk
export PATH=$PATH:$JAVA_HOME/bin:$JAVA_HOME/jre/bin
export MANPATH=$MANPATH:$JAVA_HOME/man
if [ "${{#LD_LIBRARY_PATH}}" -ne "0" ]; then
    LD_LIBRARY_PATH+=":"
fi
export LD_LIBRARY_PATH+="$JAVA_HOME/jre/lib/i386:$JAVA_HOME/jre/lib/i386/client"
export LD_LIBRARY_PATH+=":$JAVA_HOME/jre/lib/amd64:$JAVA_HOME/jre/lib/amd64/client"
""".format(java_dir=java_dir)
                )

            fi.close()
        return ret



import os.path
import collections
import shutil

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

    def builder_action_distribute(self, called_as, log):
        ret = autotools.make_high(
            self.buildingsite,
            log=log,
            options=[],
            arguments=[
                'install',
                'INSTALL_PREFIX={}'.format(self.dst_dir)
                ],
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret

    def builder_action_after_distribute(self, called_as, log):
        ret = 0

        java_dir = os.path.join(self.dst_host_multiarch_dir, 'lib', 'java')

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
                    'jvm'
                    )
                )

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
                        'jvm'
                        )
                    )

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

        return ret

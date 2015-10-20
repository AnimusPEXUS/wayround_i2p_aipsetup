
import glob
import os.path


import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std

import wayround_org.utils.file


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_actions(self):
        ret = super().define_actions()
        ret['after_distribute'] = self.builder_action_after_distribute
        return ret

    def define_custom_data(self):
        # TODO: do I need to make it install under 'opt' dir?
        return

    def builder_action_configure_define_opts(self, called_as, log):
        ret = super().builder_action_configure_define_opts(called_as, log)

        for i in ['--libdir=']:
            for j in range(len(ret) - 1, -1, -1):
                if ret[j].startswith(i):
                    del ret[j]

        ret += [

            '--with-system-cairo',
            '--with-system-icu',
            '--with-system-libxml',
            '--with-system-openldap',
            '--with-system-postgresql',

            '--enable-gtk3',
            '--disable-gtk',

            '--without-junit',

            '--with-jdk-home={}'.format(
                wayround_org.utils.path.join(
                    self.calculate_install_prefix(),
                    'opt', 'java', 'jdk'
                    )
                ),
            '--with-ant-home={}'.format(
                wayround_org.utils.path.join(
                    self.calculate_install_prefix(),
                    'opt', 'java', 'apache-ant'
                    )
                ),
            #'--with-java={}'.format(
            #    wayround_org.utils.file.which(
            #        'java',
            #        self.calculate_install_prefix()
            #        )
            #    ),
            #'--with-jvm-path={}'.format(
            #    wayround_org.utils.path.join(
            #        self.calculate_install_prefix(),
            #        'opt', 'java'
            #        )
            #    ),
            # TODO: track fixing of this
            # '--with-system-npapi-headers=no',
            #'--with-system-headers',

            # NOTE: libdir is changed, cause libreoffice uses it as install
            #       path. starting from 5.0.2

            '--libdir={}'.format(
                wayround_org.utils.path.join(
                    self.calculate_install_prefix(),
                    'opt'
                    )
                )
            ]
        return ret

    def builder_action_after_distribute(self, called_as, log):
        ret=0

        gid=glob.glob(
            wayround_org.utils.path.join(
                self.get_dst_dir(),
                'gid*'
                )
            )

        lbo_dir=wayround_org.utils.path.join(
            self.calculate_dst_install_prefix(), 'opt', 'libreoffice'
            )

        gid_dir=wayround_org.utils.path.join(
            lbo_dir,
            'gid'
            )

        lbo_lnk=wayround_org.utils.path.join(
            self.calculate_dst_install_prefix(),
            'bin',
            'soffice'
            )

        os.makedirs(
            gid_dir,
            exist_ok=True
            )

        if not os.path.isdir(gid_dir):
            ret=3
            log.error(
                "Can't create required dir: `{}'".format(gid_dir)
                )

        else:
            log.info("Moving gid* files")
            for i in gid:
                os.rename(
                    i,
                    wayround_org.utils.path.join(
                        gid_dir,
                        os.path.basename(i)
                        )
                    )

            log.info("Creating link")
            os.makedirs(
                wayround_org.utils.path.join(
                    self.calculate_dst_install_prefix(),
                    'bin'
                    )
                )

            os.symlink(
                wayround_org.utils.path.relpath(
                    wayround_org.utils.path.join(
                        lbo_dir,
                        'program',
                        'soffice'
                        ),
                    os.path.dirname(lbo_lnk)
                    ),
                lbo_lnk
                )

        return ret

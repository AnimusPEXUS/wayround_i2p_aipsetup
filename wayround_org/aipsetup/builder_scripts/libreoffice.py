
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

    def builder_action_configure_define_opts(self, called_as, log):
        ret = super().builder_action_configure_define_opts(called_as, log)
        ret += [
            '--with-system-cairo',
            '--enable-gtk3',
            '--disable-gtk',
            '--without-junit',
            # TODO: track fixing of this
            # '--with-system-npapi-headers=no',
            '--with-system-postgresql',
            #'--with-system-headers',

            ]
        return ret

    def builder_action_after_distribute(self, called_as, log):
        ret = 0

        gid = glob.glob(wayround_org.utils.path.join(self.dst_dir, 'gid*'))

        lbo_dir = wayround_org.utils.path.join(
            self.dst_host_multiarch_dir, 'lib', 'libreoffice'
            )
        gid_dir = wayround_org.utils.path.join(lbo_dir, 'gid')
        lbo_lnk = wayround_org.utils.path.join(
            self.dst_host_multiarch_dir, 'bin', 'soffice'
            )

        try:
            os.makedirs(gid_dir)
        except:
            pass

        if not os.path.isdir(gid_dir):
            ret = 3
            log.error(
                "Can't create required dir: `{}'".format(gid_dir)
                )

        else:
            log.info("Moving gid* files")
            for i in gid:
                os.rename(
                    i,
                    wayround_org.utils.path.join(
                        gid_dir, os.path.basename(i)
                        )
                    )

            log.info("Creating link")
            os.makedirs(
                wayround_org.utils.path.join(
                    self.dst_host_multiarch_dir, 'bin'
                    )
                )

            os.symlink(
                wayround_org.utils.path.relpath(
                    wayround_org.utils.path.join(
                        lbo_dir, 'program', 'soffice'
                        ),
                    os.path.dirname(lbo_lnk)
                    ),
                lbo_lnk
                )

        return ret

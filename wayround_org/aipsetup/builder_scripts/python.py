
import os.path

import wayround_org.utils.path

import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_options(self, called_as, log):

        cb_opts = []
        if self.is_crossbuild:
            cb_opts += [
                '--disable-ipv6',
                '--without-ensurepip',
                'ac_cv_file__dev_ptmx=no',
                'ac_cv_file__dev_ptc=no'
                ]

        """
            '--with-libc={}'.format(
                wayround_org.utils.path.join(
                    self.target_host_root,
                    '/usr'
                    )
                )
        """

        # f = open(os.path.join(self.src_dir, 'config.site'), 'w')
        # f.write('ac_cv_file__dev_ptmx=no\nac_cv_file__dev_ptc=no\n')
        # f.close()

        return super().builder_action_configure_define_options(called_as, log) + [
            ] + cb_opts

    def builder_action_configure_define_environment(self, called_as, log):

        # ret = {}
        # if self.is_crossbuild:
        #    ret['CONFIG_SITE'] = 'config.site'

        return {}

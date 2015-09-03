
import os.path

import wayround_org.utils.path

import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_opts(self, called_as, log):

        # f = open(wayround_org.utils.path.join(self.get_src_dir(), 'config.site'), 'w')
        # f.write('ac_cv_file__dev_ptmx=no\nac_cv_file__dev_ptc=no\n')
        # f.close()

        ret = super().builder_action_configure_define_opts(called_as, log)
        '''
        ret = self.builder_action_configure_define_opts_alternate_prefix(
            called_as, log,
            ret
            )
        '''

        cb_opts = []
        if self.get_is_crossbuild():
            cb_opts += [
                '--disable-ipv6',
                '--without-ensurepip',
                'ac_cv_file__dev_ptmx=no',
                'ac_cv_file__dev_ptc=no'
                ]

        """
            # TODO: need to figure out what is this for
            '--with-libc={}'.format(
                wayround_org.utils.path.join(
                    self.target_host_root,
                    '/usr'
                    )
                )
        """

        ret += [
            '--without-ensurepip',
            # '--with-pydebug' # NOTE: enabling may cause problems to Cython
            ]

        # NOTE: python shuld be ALLWAYS be installed in 'lib' dir. be it i?86
        #       or x86_64 build, else *.so modules will go into lib64 and
        #       python modules will remain in lib and Your system
        #       will crush because of this
        for i in range(len(ret) - 1, -1, -1):
            for j in [
                    '--libdir=',
                    ]:
                if ret[i].startswith(j):
                    del ret[i]
                    break

        ret += [
            # NOTE: at least python 2.7.10 and 3.4.3 are hard coded and can't
            #       be configured to install scripts into lib64 dir
            '--libdir=' + wayround_org.utils.path.join(
                self.calculate_install_prefix(),
                'lib'
                ),
            ]

        ret += [
            # 'SCRIPTDIR={}'.format(
            #     wayround_org.utils.path.join(
            #         self.get_host_dir(),
            #         'lib'
            #         )
            #     ),
            ] + cb_opts

        ret += cb_opts

        '''
            'DESTLIB={}'.format(
                self.get_host_lib_dir()
                ),
            'LIBDEST={}'.format(
                self.get_host_lib_dir()
                ),
        '''

        return ret

    def builder_action_build_define_args(self, called_as, log):
        ret = super().builder_action_build_define_args(called_as, log)
        ret += [
            # 'SCRIPTDIR={}'.format(
            #     wayround_org.utils.path.join(
            #         self.get_host_dir(),
            #         'lib'
            #         )
            #     ),
            ]

        return ret

    def builder_action_distribute_define_args(self, called_as, log):
        ret = super().builder_action_distribute_define_args(called_as, log)
        ret += [
            #'SCRIPTDIR={}'.format(
            #    wayround_org.utils.path.join(
            #        self.get_host_dir(),
            #        'lib'
            #        )
            #    ),
            ]
        return ret

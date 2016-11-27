

import os.path
import wayround_i2p.utils.path
import wayround_i2p.aipsetup.buildtools.autotools as autotools
import wayround_i2p.aipsetup.builder_scripts.std


class Builder(wayround_i2p.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):
        # NOTE: at least 6.0 requires regen building environment,
        #       else it will not build for non-sysroot arch
        self.forced_autogen = True
        return None

    def builder_action_configure_define_opts(self, called_as, log):
        ret = super().builder_action_configure_define_opts(called_as, log)
        ret += [
            '--with-database=gdbm',
            '--with-speex',
            '--enable-speex',
            #'--with-sysroot={}'.format(self.calculate_install_prefix())
            ]

        '''
            'LDFLAGS=-L{} -L{}'.format(
                wayround_i2p.utils.path.join(
                    self.calculate_install_prefix(),
                    'lib'
                    ),
                wayround_i2p.utils.path.join(
                    self.calculate_install_prefix(),
                    'lib64'
                    )
                )

            'PKG_CONFIG_LIBDIR={}'.format(
                ':'.join(
                    [
                        wayround_i2p.utils.path.join(
                            self.calculate_install_prefix(),
                            'lib'
                        ),
                        wayround_i2p.utils.path.join(
                            self.calculate_install_prefix(),
                            'lib64'
                        )
                    ]
                    )
                )
        '''

        return ret

    # def builder_action_build_define_args(self, called_as, log):
    #    ret = super().builder_action_build_define_args(called_as, log)
    #    ret += [
    #        ]
     #   return ret

    # def builder_action_build_define_environment(self, called_as, log):
    #    return {}

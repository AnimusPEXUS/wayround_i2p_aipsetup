

import wayround_i2p.aipsetup.builder_scripts.std
import wayround_i2p.aipsetup.builder_scripts.std_cmake
import wayround_i2p.utils.file


class Builder_old(wayround_i2p.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_opts(self, called_as, log):
        prefix = self.calculate_install_prefix()
        return [
            '--prefix=' + prefix,
            '--python={}'.format(
                wayround_i2p.utils.file.which(
                    'python',
                    under=prefix
                    )
                ),
            '--perl={}'.format(
                wayround_i2p.utils.file.which(
                    'perl',
                    under=prefix
                    )
                ),
            '--flex={}'.format(
                wayround_i2p.utils.file.which(
                    'flex',
                    under=prefix
                    )
                ),
            '--bison={}'.format(
                wayround_i2p.utils.file.which(
                    'bison',
                    under=prefix
                    )
                ),
            '--make={}'.format(
                wayround_i2p.utils.file.which(
                    'make',
                    under=prefix
                    )
                ),
            '--dot={}'.format(
                wayround_i2p.utils.file.which(
                    'dot',
                    under=prefix
                    )
                ),
            '--shared'
            ]


class Builder(wayround_i2p.aipsetup.builder_scripts.std_cmake.Builder):

    def builder_action_configure_define_opts(self, called_as, log):
        prefix = self.calculate_install_prefix()
        ret = super().builder_action_configure_define_opts(called_as, log)
        ret += [
            '-DPYTHON_EXECUTABLE={}'.format(
                wayround_i2p.utils.file.which(
                    'python3',
                    under=prefix
                    )
                ),
            #'--perl={}'.format(
            #    wayround_i2p.utils.file.which(
            #        'perl',
            #        under=prefix
            #        )
            #    ),
            '-DFLEX_EXECUTABLE={}'.format(
                wayround_i2p.utils.file.which(
                    'flex',
                    under=prefix
                    )
                ),
            '-DBISON_EXECUTABLE={}'.format(
                wayround_i2p.utils.file.which(
                    'bison',
                    under=prefix
                    )
                ),
            #'--make={}'.format(
            #    wayround_i2p.utils.file.which(
            #        'make',
            #        under=prefix
            #       )
            #    ),
            '-DDOT={}'.format(
                wayround_i2p.utils.file.which(
                    'dot',
                    under=prefix
                    )
                ),
            '-DXMLLINT={}'.format(
                wayround_i2p.utils.file.which(
                    'xmllint',
                    under=prefix
                    )
                ),

            # '--shared'
            ]

        return ret

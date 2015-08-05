

import wayround_org.aipsetup.builder_scripts.std
import wayround_org.aipsetup.builder_scripts.std_cmake
import wayround_org.utils.file


class Builder_old(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_opts(self, called_as, log):
        prefix = self.host_multiarch_dir
        return [
            '--prefix=' + prefix,
            '--python={}'.format(
                wayround_org.utils.file.which(
                    'python',
                    under=prefix,
                    exception_if_not_found=True
                    )
                ),
            '--perl={}'.format(
                wayround_org.utils.file.which(
                    'perl',
                    under=prefix,
                    exception_if_not_found=True
                    )
                ),
            '--flex={}'.format(
                wayround_org.utils.file.which(
                    'flex',
                    under=prefix,
                    exception_if_not_found=True
                    )
                ),
            '--bison={}'.format(
                wayround_org.utils.file.which(
                    'bison',
                    under=prefix,
                    exception_if_not_found=True
                    )
                ),
            '--make={}'.format(
                wayround_org.utils.file.which(
                    'make',
                    under=prefix,
                    exception_if_not_found=True
                    )
                ),
            '--dot={}'.format(
                wayround_org.utils.file.which(
                    'dot',
                    under=prefix,
                    exception_if_not_found=True
                    )
                ),
            '--shared'
            ]


class Builder(wayround_org.aipsetup.builder_scripts.std_cmake.Builder):

    def builder_action_configure_define_opts(self, called_as, log):
        prefix = self.host_multiarch_dir
        ret = super().builder_action_configure_define_opts(called_as, log)
        ret += [
            '-DPYTHON_EXECUTABLE={}'.format(
                wayround_org.utils.file.which(
                    'python3',
                    under=prefix,
                    exception_if_not_found=True
                    )
                ),
            #'--perl={}'.format(
            #    wayround_org.utils.file.which(
            #        'perl',
            #        under=prefix,
            #        exception_if_not_found=True
            #        )
            #    ),
            '-DFLEX_EXECUTABLE={}'.format(
                wayround_org.utils.file.which(
                    'flex',
                    under=prefix,
                    exception_if_not_found=True
                    )
                ),
            '-DBISON_EXECUTABLE={}'.format(
                wayround_org.utils.file.which(
                    'bison',
                    under=prefix,
                    exception_if_not_found=True
                    )
                ),
            #'--make={}'.format(
            #    wayround_org.utils.file.which(
            #        'make',
            #        under=prefix,
            #        exception_if_not_found=True
            #       )
            #    ),
            '-DDOT={}'.format(
                wayround_org.utils.file.which(
                    'dot',
                    under=prefix,
                    exception_if_not_found=True
                    )
                ),
            '-DXMLLINT={}'.format(
                wayround_org.utils.file.which(
                    'xmllint',
                    under=prefix,
                    exception_if_not_found=True
                    )
                ),

            # '--shared'
            ]

        return ret

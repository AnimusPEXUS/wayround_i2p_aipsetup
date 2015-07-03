

import wayround_org.aipsetup.builder_scripts.std
import wayround_org.utils.file

class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_options(self, called_as, log):
        prefix = '/multiarch/{}'.format(self.host)
        return [
            '--prefix='+prefix,
            '--python={}'.format(
                wayround_org.utils.file.which(
                    'python',
                    under=prefix,
                    exception_if_not_found=True
                    )
                ),
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

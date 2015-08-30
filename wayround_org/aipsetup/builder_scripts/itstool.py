

import os.path
import wayround_org.utils.path
import wayround_org.utils.file
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_opts(self, called_as, log):

        ret = super().builder_action_configure_define_opts(called_as, log)
        ret += [
            'PYTHON={}'.format(
                wayround_org.utils.file.which(
                    'python2',  
				# TODO: watch this
				# work badly with python3
                                # (Mon Aug 24 11:06:51 MSK 2015)
                    self.get_host_dir()
                    )
                ),
            ]

        return ret

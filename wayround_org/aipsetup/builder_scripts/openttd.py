

import os.path
import wayround_org.utils.path
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_opts(self, called_as, log):
        ret = super().builder_action_configure_define_opts(called_as, log)

        for i in range(len(ret) - 1, -1, -1):
            for j in [
                    '--includedir=',
                    '--libdir=',
                    '--mandir=',
                    '--sysconfdir=',
                    '--localstatedir=',
                    '--enable-shared',
                    'CC=',
                    'GCC=',
                    'CXX=',
                    '--host=',
                    '--build=',
                    ]:
                if ret[i].startswith(j):
                    del ret[i]
                    break

        ret += [
            '--strip={}'.format(wayround_org.utils.file.which(
                    'strip',
                    self.get_host_dir()
                    )
                )
            ]

        return ret

    def builder_action_distribute_define_args(self, called_as, log):
        ret = ['install', 'INSTALL_DIR={}'.format(self.get_dst_dir())]
        
        return ret

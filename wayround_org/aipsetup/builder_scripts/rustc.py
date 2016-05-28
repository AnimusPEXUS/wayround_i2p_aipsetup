

import os.path
import wayround_org.utils.path
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_opts(self, called_as, log):
        ret = super().builder_action_configure_define_opts(called_as, log)

        ret += [
            '--llvm-root={}'.format(self.get_host_dir())
            ]

        for i in ['--enable-shared']:
            while i in ret:
                ret.remove(i)

        for i in [
                'CC=', 'GCC=', 'CXX=',

                # TODO: don't know how define those for llvm and
                #       usual x86_64-pc-linux-gnu doesn't work
                #       disabling this for now
                '--host=', '--build=', '--target='
                ]:
            for j in range(len(ret) - 1, -1, -1):
                if ret[j].startswith(i):
                    del ret[j]

        return ret

    '''
    def builder_action_configure_define_environment(self, called_as, log):
        ret = super().builder_action_configure_define_environment(called_as, log)

        for i in ['CC', 'CXX']:
            if i in ret:
                del ret[i]

        return ret
    '''

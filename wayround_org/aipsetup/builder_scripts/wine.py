

import os.path
import wayround_org.utils.path
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_environment(self, called_as, log):
        res = super().builder_action_configure_define_environment(
            called_as, log
            )
        ret = res

        #for i in [
        #        'CC',
        #        'CXX',
        #        'GCC',
        #        '--host=',
        #        '--build='
        #        ]:
        #    for j in range(len(ret) - 1, -1, -1):
        #        if ret[j].startswith(i):
        #            del ret[j]

        for i in ['LD_LIBRARY_PATH', 'LIBRARY_PATH', 'PKG_CONFIG_PATH']:
            if i in res:
                ret[i] = res[i]
        return ret

    def builder_action_configure_define_opts(self, called_as, log):
        ret = super().builder_action_configure_define_opts(called_as, log)
        if self.get_arch_from_pkgi().startswith('x86_64'):
            ret += [
                '--enable-win64',
                ]
        else:
            ret += [
                #'--with-wine64=/home/agu/_LAILALO/b/wine/wine-1.7
                #.51-201509191814290421486-x86_64-pc-linux-gnu-j44
                #zu7zq/01.SOURCE'
                ]
        for i in [
                'CC=',
                'CXX=',
                'GCC=',
                '--host=',
                '--build='
                ]:
            for j in range(len(ret) - 1, -1, -1):
                if ret[j].startswith(i):
                    del ret[j]
        ret += [
            '--host=x86_64-pc-linux-gnu',
            '--build=x86_64-pc-linux-gnu'
            ]
        return ret

    def builder_action_build_define_cpu_count(self, called_as, log):
        return 1

    # def builder_action_build_define_environment(self, called_as, log):
    #    res = super().builder_action_build_define_environment(called_as, log)
    #    ret = {}
    #    for i in ['LD_LIBRARY_PATH', 'LIBRARY_PATH']:
    #        if i in res:
    #            ret[i] = res[i]
    #    return ret

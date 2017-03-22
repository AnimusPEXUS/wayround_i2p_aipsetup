

import os.path
import wayround_i2p.utils.path
import wayround_i2p.aipsetup.buildtools.autotools as autotools
import wayround_i2p.aipsetup.builder_scripts.std


class Builder(wayround_i2p.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_opts(self, called_as, log):
        ret = super().builder_action_configure_define_opts(called_as, log)

        llvm_root = ''
        if self.get_host_from_pkgi() == self.get_arch_from_pkgi():
            llvm_root = self.get_host_dir()
        else:
            llvm_root = self.get_host_arch_dir()

        ret += [
            '--llvm-root={}'.format(llvm_root),

            # trying to make build process faster
            '--enable-ccache',
            '--disable-debug',
            '--enable-optimize',

            '--enable-local-rust'
            ]

        for i in ['--enable-shared']:
            while i in ret:
                ret.remove(i)

        for i in [
                'CC=', 'GCC=', 'CXX=',

                # TODO: don't know how define those for llvm and
                #       usual x86_64-pc-linux-gnu doesn't work
                #       disabling this for now
                '--host=', '--target=', '--build='
                ]:
            for j in range(len(ret) - 1, -1, -1):
                if ret[j].startswith(i):
                    del ret[j]

        # ret.append('--build={}'.format(self.get_arch_from_pkgi()))

        return ret

    def builder_action_configure_define_environment(self, called_as, log):
        """
        This is neecec becouse else rust make script will try to use
        not 'x86_64-pc-linux-gnu' executable, but 'x86_64-pc-linux-gnu -m64' or
        simmilar, wich obviously do not exists
        """

        ret = super().builder_action_configure_define_environment(called_as, log)

        for i in ['CC', 'CXX']:
            if i in ret:
                del ret[i]

        return ret

    def builder_action_build_define_cpu_count(self, called_as, log):
        return 1

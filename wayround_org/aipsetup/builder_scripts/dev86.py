
import os.path
import wayround_org.utils.path
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):
        self.apply_host_spec_compilers_options = True
        return

    def define_actions(self):
        ret = super().define_actions()
        del(ret['autogen'])
        del(ret['configure'])
        return ret

    def builder_action_build_define_cpu_count(self, called_as, log):
        # dev86 does not supports multithreaded builds
        return 1

    def builder_action_build_define_args(self, called_as, log):
        return self.all_automatic_flags_as_list()

    def builder_action_distribute_define_args(self, called_as, log):

        #lib_bcc_dir = wayround_org.utils.path.join(
        #    '/..',
        #    '..',
        #    'lib',#self.calculate_main_multiarch_lib_dir_name(),
        #    'bcc'
        #    )

        dst_dir = self.calculate_dst_install_prefix()

        ret = [
            'install',
            'PREFIX=/',
            'DESTDIR={}'.format(dst_dir),
            'DIST={}'.format(dst_dir),
            #'BINDIR=/bin',
            #'LIBDIR={}'.format(lib_bcc_dir),
            #'INCLDIR={}'.format(lib_bcc_dir),
            #'ASLDDIR=/bin',
            #'MANDIR=/share/man',
            #'INDAT=', 'INEXE='
            ]
        return ret

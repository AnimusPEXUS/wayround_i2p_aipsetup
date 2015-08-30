

import os.path
import wayround_org.utils.path
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_opts(self, called_as, log):
        ret = super().builder_action_configure_define_opts(called_as, log)
        ret += [
            '--disable-rpath',
            '--disable-fast-install',
            '--enable-dependency-tracking',
            '--enable-introspection=yes',
            '--with-gnu-ld',
            '--disable-examples',
            '--disable-fatal-warnings',
            #'--disable-audiotestsrc',
            #'--disable-videotestsrc',
            #'--disable-freetypetest',
            #'--with-sysroot={}'.format(self.get_host_dir())
            ]
        return ret

    def builder_action_build_define_environment(self, called_as, log):
        ret = super().builder_action_build_define_environment(called_as, log)
        # ret['LD_LIBRARY_PATH'] += ':../tag/.libs'
        return ret

   # def builder_action_build_define_add_args(self, called_as, log):
    #    #ret = ['LDFLAGS=-l']
    #    return ret

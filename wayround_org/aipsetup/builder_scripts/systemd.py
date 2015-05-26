
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    # NOTE: configure time  'CFLAGS': '-fno-lto' environment may be required

    def builder_action_configure_define_options(self, log):
        return super().builder_action_configure_define_options(log) + [
            # '--disable-silent-rules',
            '--enable-gtk-doc',
            '--enable-logind',
            '--enable-microhttpd',
            '--enable-qrencode',
            # '--enable-static',
            # '--disable-tests',
            # '--disable-coverage',
            '--enable-shared',
            '--enable-compat-libs',
            ]

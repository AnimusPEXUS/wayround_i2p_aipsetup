
import os.path

import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    # NOTE: configure time  'CFLAGS': '-fno-lto' environment may be required

    def builder_action_configure_define_opts(self, called_as, log):
        ret = super().builder_action_configure_define_opts(called_as, log)
        ret += [
            # '--disable-silent-rules',
            '--enable-gudev',
            '--enable-gtk-doc=auto',
            '--enable-logind=auto',
            '--enable-microhttpd=auto',
            '--enable-qrencode=auto',
            # '--enable-static',
            # '--disable-tests',
            # '--disable-coverage',
            '--enable-shared',
            '--enable-compat-libs',
            '--with-libgcrypt-prefix={}'.format(self.host_multiarch_dir)
            ]
        ret += [
            '--with-pamlibdir={}'.format(
                os.path.join(
                    self.host_multiarch_dir,
                    'lib',
                    'security'
                    )
                )
            ]
        return ret


import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    # NOTE: configure time  'CFLAGS': '-fno-lto' environment may be required

    def builder_action_configure_define_options(self, called_as, log):
        pamlibdir=[]
        if '64' in self.host:
            pamlibdir+=['--with-pamlibdir=/usr/lib64/security']
        return super().builder_action_configure_define_options(log) + [
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
            ] + pamlibdir

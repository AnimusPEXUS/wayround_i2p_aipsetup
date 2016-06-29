

import os.path
import wayround_org.utils.path
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_patch(self, called_as, log):
        ret = 0
        try:

            file_name = wayround_org.utils.path.join(
                self.get_src_dir(),
                'plugins',
                'Makefile'
                )

            with open(file_name) as mf:
                _l = mf.read().splitlines()

            for i in range(len(_l)):

                if _l[i] == "INSTALL\t= install -o root":
                    _l[i] = "INSTALL = install"

                if _l[i] == "\t$(INSTALL) -d $(LIBDIR)":
                    _l[i] = "\t$(INSTALL) -d $(DESTDIR)/$(LIBDIR)"

                if _l[i] == "\t$(INSTALL) $? $(LIBDIR)":
                    _l[i] = "\t$(INSTALL) $? $(DESTDIR)/$(LIBDIR)"

            with open(file_name, 'w') as mf:
                mf.write('\n'.join(_l))

        except:
            logging.exception("Can't patch Makefile")
            ret = 40
        return ret

    def builder_action_configure_define_opts(self, called_as, log):
        ret = super().builder_action_configure_define_opts(called_as, log)
        ret += [
            '--with-system-nspr',
            '--enable-threadsafe',
            ]
        return ret

    def builder_action_distribute_define_args(self, called_as, log):
        ret = super().builder_action_distribute_define_args(called_as, log)
        ret += ['INSTALL=install']
        return ret

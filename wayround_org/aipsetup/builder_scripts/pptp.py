

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
        ret['patch'] = self.builder_action_patch
        return ret

    def builder_action_patch(self, called_as, log):
        ret = 0
        try:
            mf = open(wayround_org.utils.path.join(self.get_src_dir(), 'Makefile'))

            _l = mf.read().splitlines()

            mf.close()

            for i in range(len(_l)):

                if _l[i].startswith(
                        "\tinstall -o root -m 555 pptp $(BINDIR)"
                        ):
                    _l[i] = "\tinstall pptp $(BINDIR)"

                if _l[i].startswith(
                        "\tinstall -o root -m 555 pptpsetup $(BINDIR)"
                        ):
                    _l[i] = "\tinstall pptpsetup $(BINDIR)"

            mf = open(wayround_org.utils.path.join(self.get_src_dir(), 'Makefile'), 'w')
            mf.write('\n'.join(_l))
            mf.close()
        except:
            logging.exception("Can't patch Makefile")
            ret = 40
        return ret

    def builder_action_build_define_opts(self, called_as, log):
        ret = super().builder_action_build_define_opts()
        ret += self.all_automatic_flags_as_list()
        return ret

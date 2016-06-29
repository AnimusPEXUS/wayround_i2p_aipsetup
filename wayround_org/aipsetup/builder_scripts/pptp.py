

import os.path
import wayround_org.utils.path
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):
        self.apply_host_spec_compilers_options = True

        '''
        BINDIR=$(DESTDIR)/usr/sbin
        MANDIR=$(DESTDIR)/usr/share/man/man8
        PPPDIR=$(DESTDIR)/etc/ppp
        '''

        dst_prefix = self.calculate_dst_install_prefix()

        ret = {
            'PPPD': wayround_org.utils.file.which(
                'pppd',
                self.calculate_install_prefix()
                ),
            'BINDIR': wayround_org.utils.path.join(dst_prefix, 'sbin'),
            'MANDIR': wayround_org.utils.path.join(
                dst_prefix,
                'share',
                'man',
                'man8'
                ),
            #'PPPDIR': wayround_org.utils.path.join(dst_prefix, 'etc', 'ppp')
            }
        return ret

    def define_actions(self):
        ret = super().define_actions()
        del(ret['autogen'])
        del(ret['configure'])
        #ret['patch'] = self.builder_action_patch
        return ret

    def builder_action_patch(self, called_as, log):
        ret = 0
        try:

            file_name = wayround_org.utils.path.join(
                self.get_src_dir(),
                'Makefile'
                )

            with open(file_name) as mf:
                _l = mf.read().splitlines()

            for i in range(len(_l)):

                if _l[i].startswith(
                        "\tinstall -o root -m 555 pptp $(BINDIR)"
                        ):
                    _l[i] = "\tinstall pptp $(BINDIR)"

                if _l[i].startswith(
                        "\tinstall -o root -m 555 pptpsetup $(BINDIR)"
                        ):
                    _l[i] = "\tinstall pptpsetup $(BINDIR)"

            with open(file_name, 'w') as mf:
                mf.write('\n'.join(_l))

        except:
            logging.exception("Can't patch Makefile")
            ret = 40
        return ret

    def builder_action_build_define_opts(self, called_as, log):
        ret = super().builder_action_build_define_opts(called_as, log)
        ret += self.all_automatic_flags_as_list()
        return ret

    def builder_action_distribute_define_args(self, called_as, log):
        ret = super().builder_action_distribute_define_args(called_as, log)
        ret += [
            'BINDIR={}'.format(self.custom_data['BINDIR']),
            'MANDIR={}'.format(self.custom_data['MANDIR']),
            #'PPPDIR={}'.format(self.custom_data['PPPDIR']),
            ]
        return ret


import os.path
import shutil

import wayround_org.utils.file
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_actions(self):
        ret = super().define_actions()
        ret['after_distribute'] = self.builder_action_after_distribute
        return ret

    def builder_action_configure_define_opts(self, called_as, log):
        ret = super().builder_action_configure_define_opts(called_as, log)
        ret += [
            # '--disable-silent-rules',
            '--enable-gudev=auto',
            '--enable-gtk-doc=auto',
            '--enable-logind=auto',
            '--enable-microhttpd=auto',
            '--enable-qrencode=auto',
            # '--enable-static',
            # '--disable-tests',
            # '--disable-coverage',
            '--enable-shared',
            '--enable-compat-libs',
            #'--with-libgcrypt-prefix={}'.format(self.get_host_dir()),
            #'--with-rootprefix={}'.format(self.get_host_dir()),
            ]
        ret += [
            '--with-pamlibdir={}'.format(
                wayround_org.utils.path.join(
                    self.calculate_install_prefix(),
                    'lib',
                    'security'
                    )
                )
            ]
        ret += [
            'PYTHON={}'.format(
                wayround_org.utils.file.which(
                    'python',
                    self.calculate_install_prefix()
                    )
                )
            ]
        return ret

    def builder_action_after_distribute(self, called_as, log):

        ret = 0

        sd = wayround_org.utils.path.join(
            self.get_dst_dir(),
            'usr'
            )

        dd = self.calculate_dst_install_prefix()

        if os.path.isdir(dd):

            ret = wayround_org.utils.file.copytree(
                sd,
                dd,
                dst_must_be_empty=False,
                verbose=False
                )

            if ret == 0:
                shutil.rmtree(sd)

        else:
            log.error("error")
            raise Exception("This should not usualy happen")

        return ret

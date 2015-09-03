
import os.path
import subprocess

import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.utils.file

import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):
        return {}

    def define_actions(self):
        ret = super().define_actions()
        ret['sh_link'] = self.builder_action_sh_link
        return ret

    def builder_action_patch(self, called_as, log):
        ret = 0
        patches = os.listdir(self.get_patches_dir())

        if len(patches) == 0:
            log.error("provide patches!")
            ret = 30
        else:

            patches2 = []

            for i in patches:
                if not i.endswith('.sig'):
                    patches2.append(i)

            patches = patches2
            del patches2

            patches.sort()

            for i in patches:
                log.info("Patching using {}".format(i))
                if subprocess.Popen(
                        ['patch',
                         '-i',
                         wayround_org.utils.path.join(
                             self.get_patches_dir(),
                             i),
                            '-p0'],
                        cwd=self.get_src_dir()
                        ).wait() != 0:
                    log.error("Patch error")
                    ret = 1
        return ret

    def builder_action_configure_define_opts(self, called_as, log):

        ret = super().builder_action_configure_define_opts(called_as, log)

        ret += [
            '--enable-multibyte',
            '--with-curses'
            ]

        if not self.get_is_crossbuild() and not self.get_is_crossbuilder():
            pass
        else:
            ret += [
                '--without-curses',
                # '--disable-readline' # NOTE: this maybe required for new
                #                              build
                ]

        return ret

    def builder_action_sh_link(self, called_as, log):
        tsl = wayround_org.utils.path.join(
            self.calculate_dst_install_prefix(), 'bin', 'sh'
            )

        if os.path.exists(tsl) or os.path.islink(tsl):
            os.unlink(tsl)

        os.symlink('bash', tsl)
        return 0

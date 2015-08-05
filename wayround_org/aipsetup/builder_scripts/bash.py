
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
        patches = os.listdir(self.patches_dir)

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
                         os.path.join(self.patches_dir, i),
                         '-p0'],
                        cwd=self.src_dir
                        ).wait() != 0:
                    log.error("Patch error")
                    ret = 1
        return ret

    def builder_action_configure_define_opts(self, called_as, log):
        ret = [
            '--enable-multibyte',
            '--with-curses'
            ]

        if not self.is_crossbuild and not self.is_crossbuilder:
            pass
        else:
            ret += [
                '--without-curses',
                # '--disable-readline' # NOTE: this maybe required for new
                #                              build
                ]

        return super().builder_action_configure_define_opts(
            called_as, log) + ret

    def builder_action_sh_link(self, called_as, log):
        tsl = wayround_org.utils.path.join(
            self.dst_host_multiarch_dir, 'bin', 'sh'
            )

        if os.path.exists(tsl) or os.path.islink(tsl):
            os.unlink(tsl)

        os.symlink('bash', tsl)
        return 0

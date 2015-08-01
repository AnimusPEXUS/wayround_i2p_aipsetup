

import os.path
import subprocess

import wayround_org.utils.path
import wayround_org.utils.file
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_actions(self):
        ret = super().define_actions()
        del(ret['autogen'])
        return ret

    def builder_action_configure(self, called_as, log):
        p = subprocess.Popen(
            [wayround_org.utils.file.which('perl', self.host_multiarch_dir),
                'Makefile.PL'],  # TODO: host dependent actions required
            cwd=self.src_dir,
            stdout=log.stdout,
            stderr=log.stderr
            )
        ret = p.wait()
        return ret

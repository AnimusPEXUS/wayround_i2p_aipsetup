

import os.path
import subprocess

import wayround_i2p.utils.path
import wayround_i2p.aipsetup.buildtools.autotools as autotools
import wayround_i2p.aipsetup.builder_scripts.std


class Builder(wayround_i2p.aipsetup.builder_scripts.std.Builder):

    def define_actions(self):
        ret = super().define_actions()
        del(ret['autogen'])
        return ret

    def builder_action_configure(self, called_as, log):
        p = subprocess.Popen(
            ['bash', 'setup.sh'],
            cwd=wayround_i2p.utils.path.join(self.get_src_dir(), 'sys', 'unix'),
            stdout=log.stdout,
            stderr=log.stderr
            )
        ret = p.wait()
        return ret

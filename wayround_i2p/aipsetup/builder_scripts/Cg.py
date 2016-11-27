
import os.path
import shutil

import wayround_i2p.aipsetup.build
import wayround_i2p.aipsetup.build_scripts.std_simple_makefile
import wayround_i2p.aipsetup.buildtools.autotools as autotools
import wayround_i2p.utils.file


class Builder(wayround_i2p.aipsetup.build_scripts.std_simple_makefile):

    def builder_action_distribute(self, called_as, log):

        ret = 0

        for i in ['bin', 'include', 'lib', 'lib64', 'libx32']:
            if ret != 0:
                break

            jo = wayround_i2p.utils.path.join(self.get_src_dir(), i)

            if os.path.exists(jo):

                try:
                    shutil.move(
                        jo,
                        wayround_i2p.utils.path.join(
                            self.calculate_dst_install_prefix()
                            )
                        )
                except:
                    log.exception(
                        "Error moving `{}' dir into dest".format(i)
                        )
                    ret = 5

        return ret

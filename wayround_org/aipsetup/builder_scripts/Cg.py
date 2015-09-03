
import os.path
import shutil

import wayround_org.aipsetup.build
import wayround_org.aipsetup.build_scripts.std_simple_makefile
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.utils.file


class Builder(wayround_org.aipsetup.build_scripts.std_simple_makefile):

    def builder_action_distribute(self, called_as, log):

        ret = 0

        for i in ['bin', 'include', 'lib', 'lib64', 'libx32']:
            if ret != 0:
                break

            jo = wayround_org.utils.path.join(self.get_src_dir(), i)

            if os.path.exists(jo):

                try:
                    shutil.move(
                        jo,
                        wayround_org.utils.path.join(
                            self.calculate_dst_install_prefix()
                            )
                        )
                except:
                    log.exception(
                        "Error moving `{}' dir into dest".format(i)
                        )
                    ret = 5

        return ret


import os.path
import shutil

import wayround_org.aipsetup.build
import wayround_org.aipsetup.build_scripts.std_simple_makefile
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.utils.file


class Builder(wayround_org.aipsetup.build_scripts.std_simple_makefile):

    def builder_action_distribute(self, called_as, log):

        ret = 0

        for i in ['bin', 'include', 'lib']:
            if ret != 0:
                break

            try:
                shutil.move(
                    os.path.join(self.src_dir, i),
                    os.path.join(self.dst_dir, 'usr')
                    )
            except:
                log.exception(
                    "Error moving `{}' dir into dest".format(i)
                    )
                ret = 5

        return ret

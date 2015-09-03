

import os.path
import wayround_org.utils.path
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_patch(self, called_as, log):

        ret = 0

        try:
            f = open(
                wayround_org.utils.path.join(
                    self.get_src_dir(),
                    makefile_am
                    )
                )

            lines = f.read().splitlines()

            f.close()

            for i in range(len(lines)):

                if lines[i] == 'man8dir\t  = $(mandir)/man8':
                    lines[i] = 'man_MANS = install-catalog.8'

                if lines[i] == 'man8_DATA = *.8':
                    lines[i] = ''

            f = open(
                wayround_org.utils.path.join(
                    self.get_src_dir(),
                    makefile_am
                    ),
                'w'
                )

            f.write('\n'.join(lines))

            f.close()

        except:
            logging.exception("Error")
            ret = 1

        return ret

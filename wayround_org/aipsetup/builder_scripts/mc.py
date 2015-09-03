
import shutil
import glob
import os.path

import wayround_org.aipsetup.buildtools.autotools as autotools

import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_actions(self):
        ret = super().define_actions()
        ret['asc_support'] = self.builder_action_asc_support
        return ret

    def builder_action_asc_support(self, called_as, log):
        exts_file = wayround_org.utils.path.join(
            self.get_dst_dir(),
            'etc',
            'mc',
            'mc.ext'
            )

        f = open(exts_file)
        ftl = f.readlines()
        f.close()

        if not '# asp\n' in ftl:

            log.info("Adding ASP support")

            ind = ftl.index('# tar\n')

            ind = ftl.index('\n', ind)

            ftl = (ftl[:ind] + [
                """
# asp
shell/i/.asp
\tOpen=%cd %p/utar://
\tView=%view{{ascii}} {prefix}/libexec/mc/ext.d/archive.sh view tar
""".format(
                    prefix=self.calculate_install_prefix()
                    )
                ] + ftl[ind:]
                )

            f = open(exts_file, 'w')
            f.writelines(ftl)
            f.close()

        else:

            log.info("ASC support already on place")

        return 0

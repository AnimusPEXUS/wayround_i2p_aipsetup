
import shutil
import glob
import os.path

import wayround_org.aipsetup.buildtools.autotools as autotools

import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_actions(self):
        ret = super().define_actions()
        ret['wrapper'] = self.builder_action_wrapper
        ret['asc_support'] = self.builder_action_asc_support
        return ret

    def builder_action_wrapper(self, log):

        set_dir = os.path.join(self.dst_dir, 'etc', 'profile.d', 'SET')

        bin_dir = os.path.join(self.dst_dir, 'usr', 'share', 'mc', 'bin')

        os.makedirs(set_dir, exist_ok=True)

        os.makedirs(bin_dir, exist_ok=True)

        files = glob.glob(os.path.join(self.src_dir, 'contrib', '*.sh'))

        for i in files:
            shutil.copy(i, bin_dir)

        f = open(os.path.join(set_dir, '009.mc'), 'w')
        f.write(
            """\
#!/bin/bash
alias mc=". /usr/share/mc/bin/mc-wrapper.sh"
"""
            )
        f.close()

        return 0

    def builder_action_asc_support(self, log):
        exts_file = os.path.join(self.dst_dir, 'etc', 'mc', 'mc.ext')

        f = open(exts_file)
        ftl = f.readlines()
        f.close()

        if not '# asc\n' in ftl:

            log.info("Adding ASC support")

            ind = ftl.index('# tar\n')

            ind = ftl.index('\n', ind)

            ftl = (ftl[:ind] + [
                '\n',
                '# asp\n',
                'shell/i/.asp\n'
                '\tOpen=%cd %p/utar://\n'
                '\tView=%view{ascii} /usr/libexec/mc/ext.d/archive.sh view tar\n'
                ] +
                ftl[ind:])

            f = open(exts_file, 'w')
            f.writelines(ftl)
            f.close()

        else:

            log.info("ASC support already on place")

        return 0


import logging
import os.path
import subprocess

import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.utils.file


import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_patch(self, log):

        ret = 0

        if (self.package_info['pkg_nameinfo']['groups']['version_dirty']
                == '2.00'):

            fn = self.src_dir + '/grub-core/gnulib/stdio.in.h'

            f = open(fn)
            ftl = f.readlines()
            f.close()

            for i in ftl:
                if 'gets is a' in i:
                    ftl.remove(i)
                    break

            f = open(fn, 'w')
            f.writelines(ftl)
            f.close()

            fn = self.src_dir + '/util/grub-mkfont.c'

            f = open(fn)
            ftl = f.readlines()
            f.close()

            for i in range(len(ftl)):
                if ftl[i] == '#include <freetype/ftsynth.h>\n':
                    ftl[i] = '#include <freetype2/ftsynth.h>\n'
                    break

            f = open(fn, 'w')
            f.writelines(ftl)
            f.close()

            """

            p = subprocess.Popen(
                ['sed',
                 '-i',
                 '-e',
                 '/gets is a/d',
                 'grub-core/gnulib/stdio.in.h'
                 ],
                cwd=self.src_dir,
                stdout=log.stdout,
                stderr=log.stderr
                )
            ret = p.wait()

            p = subprocess.Popen(
                ['sed',
                 '-i',
                 '-e',
                 '/gets is a/d',
                 'grub-core/gnulib/stdio.in.h'
                 ],
                cwd=self.src_dir,
                stdout=log.stdout,
                stderr=log.stderr
                )
            ret = p.wait()

            """

        return ret

    def builder_action_configure_define_options(self, log):
        return super().builder_action_configure_define_options(log) + [
            '--disable-werror'
            ]

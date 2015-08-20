
import os.path
import subprocess

import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.utils.file


import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_patch(self, called_as, log):

        ret = 0

        if (self.get_package_info()['pkg_nameinfo']['groups']['version_dirty']
                == '2.00'):

            fn = self.get_src_dir() + '/grub-core/gnulib/stdio.in.h'

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

            fn = self.get_src_dir() + '/util/grub-mkfont.c'

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
                cwd=self.get_src_dir(),
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
                cwd=self.get_src_dir(),
                stdout=log.stdout,
                stderr=log.stderr
                )
            ret = p.wait()

            """

        return ret

    def builder_action_configure_define_opts(self, called_as, log):
        return super().builder_action_configure_define_opts(called_as, log) + [
            '--disable-werror'
            ]

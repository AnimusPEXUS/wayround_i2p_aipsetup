
import logging
import os.path
import subprocess

import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.utils.file

import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_patch(self, called_as, log):

        # disabled patching for experiment
        return 0

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

"""
def main(buildingsite, action=None):

    ret = 0

    r = wayround_org.aipsetup.build.build_script_wrap(
        buildingsite,
        ['extract', 'patch', 'configure', 'build', 'distribute'],
        action,
        "help"
        )

    if not isinstance(r, tuple):
        logging.error("Error")
        ret = r

    else:

        pkg_info, actions = r

        src_dir = wayround_org.aipsetup.build.getDIR_SOURCE(buildingsite)

        dst_dir = wayround_org.aipsetup.build.getDIR_DESTDIR(buildingsite)

        separate_build_dir = False

        source_configure_reldir = '.'

        if 'extract' in actions:
            if os.path.isdir(src_dir):
                logging.info("cleaningup source dir")
                wayround_org.utils.file.cleanup_dir(src_dir)
            ret = autotools.extract_high(
                buildingsite,
                pkg_info['pkg_info']['basename'],
                unwrap_dir=True,
                rename_dir=False
                )

        if 'patch' in actions and ret == 0:
            p = subprocess.Popen(
                ['sed', '-i', '-e', '/gets is a/d', 'lib/stdio.in.h'],
                cwd=src_dir
                )
            ret = p.wait()

        if 'configure' in actions and ret == 0:
            ret = autotools.configure_high(
                buildingsite,
                options=[
                    '--prefix=' + pkg_info['constitution']['paths']['usr'],
                    '--mandir=' + pkg_info['constitution']['paths']['man'],
                    '--sysconfdir=' +
                    pkg_info['constitution']['paths']['config'],
                    '--localstatedir=' +
                    pkg_info['constitution']['paths']['var'],
                    '--enable-shared',
                    '--host=' + pkg_info['constitution']['host'],
                    '--build=' + pkg_info['constitution']['build'],
                    #                    '--target=' + pkg_info['constitution']['target']
                    ],
                arguments=[],
                environment={},
                environment_mode='copy',
                source_configure_reldir=source_configure_reldir,
                use_separate_buildding_dir=separate_build_dir,
                script_name='configure',
                run_script_not_bash=False,
                relative_call=False
                )

        if 'build' in actions and ret == 0:
            ret = autotools.make_high(
                buildingsite,
                options=[],
                arguments=[],
                environment={},
                environment_mode='copy',
                use_separate_buildding_dir=separate_build_dir,
                source_configure_reldir=source_configure_reldir
                )

        if 'distribute' in actions and ret == 0:
            ret = autotools.make_high(
                buildingsite,
                options=[],
                arguments=[
                    'install',
                    'DESTDIR=' + dst_dir
                    ],
                environment={},
                environment_mode='copy',
                use_separate_buildding_dir=separate_build_dir,
                source_configure_reldir=source_configure_reldir
                )

    return ret
"""
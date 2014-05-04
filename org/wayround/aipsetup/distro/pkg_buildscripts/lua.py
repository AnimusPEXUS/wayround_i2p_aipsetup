
import logging
import os.path
import subprocess

import org.wayround.aipsetup.build
import org.wayround.aipsetup.buildtools.autotools as autotools
import org.wayround.utils.file


def main(buildingsite, action=None):

    ret = 0

    r = org.wayround.aipsetup.build.build_script_wrap(
        buildingsite,
        ['extract', 'build', 'distribute', 'pc'],
        action,
        "help"
        )

    if not isinstance(r, tuple):
        logging.error("Error")
        ret = r

    else:

        pkg_info, actions = r

        src_dir = org.wayround.aipsetup.build.getDIR_SOURCE(buildingsite)

        dst_dir = org.wayround.aipsetup.build.getDIR_DESTDIR(buildingsite)

        separate_build_dir = False

        source_configure_reldir = '.'

        if 'extract' in actions:
            if os.path.isdir(src_dir):
                logging.info("cleaningup source dir")
                org.wayround.utils.file.cleanup_dir(src_dir)
            ret = autotools.extract_high(
                buildingsite,
                pkg_info['pkg_info']['basename'],
                unwrap_dir=True,
                rename_dir=False
                )

        if 'build' in actions and ret == 0:
            ret = autotools.make_high(
                buildingsite,
                options=[],
                arguments=['linux', 'INSTALL_TOP=/usr'],
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
                    'INSTALL_TOP=' + os.path.join(dst_dir, 'usr')
                    ],
                environment={},
                environment_mode='copy',
                use_separate_buildding_dir=separate_build_dir,
                source_configure_reldir=source_configure_reldir
                )

        if 'pc' in actions and ret == 0:

            pc_file_name_dir = org.wayround.utils.path.join(
                dst_dir, 'usr', 'lib', 'pkgconfig'
                )

            try:
                os.makedirs(pc_file_name_dir)
            except FileExistsError:
                pass

            pc_file_name = org.wayround.utils.path.join(
                pc_file_name_dir, 'lua.pc'
                )

            pc_file = open(pc_file_name, 'w')

            pc_text = ''

            p = subprocess.Popen(
                ['make',
                 'pc',
                 'INSTALL_TOP=' + org.wayround.utils.path.join('/', 'usr')
                 ],
                stdout=subprocess.PIPE,
                cwd=src_dir
                )
            p.wait()
            pc_text = p.communicate()[0]
            pc_text = str(pc_text, 'utf-8')
            pc_lines = pc_text.splitlines()

            version = []
#            print("Out: {}".format(pc_text))

            for i in pc_lines:
                if i.startswith('version='):
                    version = i.split('=')[1].split('.')

            tpl = """\
V={V}
R={R}

prefix=/usr
INSTALL_BIN=${{prefix}}/bin
INSTALL_INC=${{prefix}}/include
INSTALL_LIB=${{prefix}}/lib
INSTALL_MAN=${{prefix}}/man/man1
INSTALL_LMOD=${{prefix}}/share/lua/${{V}}
INSTALL_CMOD=${{prefix}}/lib/lua/${{V}}
exec_prefix=${{prefix}}
libdir=${{exec_prefix}}/lib
includedir=${{prefix}}/include

Name: Lua
Description: An Extensible Extension Language
Version: ${{R}}
Requires:
Libs: -L${{libdir}} -llua -lm
Cflags: -I${{includedir}}
""".format(
                V='.'.join(version[:2]),
                R='.'.join(version)
                )

            pc_file.write(tpl)
            pc_file.close()

    return ret

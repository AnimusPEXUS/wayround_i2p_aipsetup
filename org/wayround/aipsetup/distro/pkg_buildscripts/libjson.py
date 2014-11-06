
import logging
import os.path

import org.wayround.aipsetup.build
import org.wayround.aipsetup.buildtools.autotools as autotools
import org.wayround.utils.file


def main(buildingsite, action=None):

    ret = 0

    r = org.wayround.aipsetup.build.build_script_wrap(
        buildingsite,
        [
            'extract', 'patch',
            'build_a', 'distribute_a',
            'build_so', 'distribute_so'
            ],
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

        if 'patch' in actions and ret == 0:
            f = open(os.path.join(src_dir, 'makefile'))
            lines = f.read().split('\n')
            f.close()

            for i in range(len(lines)):
            
                if lines[i] == '\tldconfig':
                    lines[i] = '#\tldconfig'
                    
                if lines[i] == '\tcp -rv $(srcdir)/Dependencies/ $(include_path)/$(libname_hdr)/$(srcdir)':
                    lines[i] = '\tcp -rv $(srcdir)/../Dependencies/ $(include_path)/$(libname_hdr)/$(srcdir)'

            f = open(os.path.join(src_dir, 'makefile'), 'w')
            f.write('\n'.join(lines))
            f.close()

        if 'build_a' in actions and ret == 0:
            ret = autotools.make_high(
                buildingsite,
                options=[],
                arguments=[],
                environment={},
                environment_mode='copy',
                use_separate_buildding_dir=separate_build_dir,
                source_configure_reldir=source_configure_reldir
                )

        if 'distribute_a' in actions and ret == 0:
            try:
                os.makedirs(os.path.join(dst_dir, 'usr', 'lib'))
            except:
                pass

            ret = autotools.make_high(
                buildingsite,
                options=[],
                arguments=[
                    'install',
                    'prefix=' + os.path.join(dst_dir, 'usr')
                    ],
                environment={},
                environment_mode='copy',
                use_separate_buildding_dir=separate_build_dir,
                source_configure_reldir=source_configure_reldir
                )

        if 'build_so' in actions and ret == 0:
            ret = autotools.make_high(
                buildingsite,
                options=[],
                arguments=['SHARED=1'],
                environment={},
                environment_mode='copy',
                use_separate_buildding_dir=separate_build_dir,
                source_configure_reldir=source_configure_reldir
                )

        if 'distribute_so' in actions and ret == 0:
            try:
                os.makedirs(os.path.join(dst_dir, 'usr', 'lib'))
            except:
                pass

            ret = autotools.make_high(
                buildingsite,
                options=[],
                arguments=[
                    'install',
                    'prefix=' + os.path.join(dst_dir, 'usr'),
                    'SHARED=1'
                    ],
                environment={},
                environment_mode='copy',
                use_separate_buildding_dir=separate_build_dir,
                source_configure_reldir=source_configure_reldir
                )

    return ret

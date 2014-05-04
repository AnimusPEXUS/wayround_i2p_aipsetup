
import logging
import os.path

import org.wayround.aipsetup.build
import org.wayround.aipsetup.buildtools.autotools as autotools
import org.wayround.utils.file


def main(buildingsite, action=None):

    ret = 0

    r = org.wayround.aipsetup.build.build_script_wrap(
        buildingsite,
        ['extract', 'configure', 'build',
         'distribute1',
         'distribute2',
         'distribute3'
         # 'fix_symlinks', 'fix_la_file'
         ],
        action,
        "help"
        )

    if not isinstance(r, tuple):
        logging.error("Error")
        ret = r

    else:

        pkg_info, actions = r

        basename = pkg_info['pkg_info']['basename']

        logging.info(
                "Detected (and accepted) basename is: [{}]".format(basename)
                )

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

        if 'configure' in actions and ret == 0:
            ret = autotools.configure_high(
                buildingsite,
                options=[
                    '--prefix=' +
                        pkg_info['constitution']['paths']['usr'],
                    '--mandir=' +
                        pkg_info['constitution']['paths']['man'],
                    '--sysconfdir=' +
                        pkg_info['constitution']['paths']['config'],
                    '--localstatedir=' +
                        pkg_info['constitution']['paths']['var'],
#                    '--prefix=' + os.path.join(dst_dir, 'usr'),
#                    '--mandir=' +
#                        os.path.join(dst_dir, 'usr', 'share', 'man'),
#                    '--sysconfdir=' + os.path.join(dst_dir, 'etc'),
#                    '--localstatedir=' + os.path.join(dst_dir, 'var'),
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

        if 'distribute1' in actions and ret == 0:

            commands = ['install']

            ret = autotools.make_high(
                buildingsite,
                options=[],
                arguments=commands + [
                    'DESTDIR=' + dst_dir
                    ],
                environment={},
                environment_mode='copy',
                use_separate_buildding_dir=separate_build_dir,
                source_configure_reldir=source_configure_reldir
                )

        if 'distribute2' in actions and ret == 0:

            commands = ['install-dev']

            ret = autotools.make_high(
                buildingsite,
                options=[],
                arguments=commands + [
                    'DESTDIR=' + dst_dir
                    ],
                environment={},
                environment_mode='copy',
                use_separate_buildding_dir=separate_build_dir,
                source_configure_reldir=source_configure_reldir
                )

        if 'distribute3' in actions and ret == 0:

            commands = []

            if not basename in ['xfsprogs', 'xfsdump', 'dmapi']:
                commands.append('install-lib')

            ret = autotools.make_high(
                buildingsite,
                options=[],
                arguments=commands + [
                    'DESTDIR=' + dst_dir
                    ],
                environment={},
                environment_mode='copy',
                use_separate_buildding_dir=separate_build_dir,
                source_configure_reldir=source_configure_reldir
                )

#        if ('fix_symlinks' in actions
#            and ret == 0
#            and not basename in ['xfsprogs', 'xfsdump', 'dmapi']):
#
#            try:
#                for i in [
#                    'lib{}.a'.format(basename),
#                    'lib{}.la'.format(basename)
#                    ]:
#                    ffn = os.path.join(dst_dir, 'usr', 'lib', i)
#
#                    if os.path.exists(ffn):
#                        os.unlink(ffn)
#
#                    os.symlink(os.path.join('..', 'libexec', i), ffn)
#
#                for i in ['lib{}.so'.format(basename)]:
#                    ffn = os.path.join(dst_dir, 'usr', 'libexec', i)
#
#                    if os.path.exists(ffn):
#                        os.unlink(ffn)
#
#                    os.symlink(os.path.join('..', 'lib', i), ffn)
#            except:
#                logging.exception('error')
#                ret = 1
#
#        if ('fix_la_file' in actions
#            and ret == 0
#            and not basename in ['xfsprogs', 'xfsdump', 'dmapi']):
#
#            la_file_name = os.path.join(
#                dst_dir, 'usr', 'lib', 'lib{}.la'.format(basename)
#                )
#
#            print("la_file_name == {}".format(la_file_name))
#
#            la_file = open(la_file_name)
#            lines = la_file.read().splitlines()
#            la_file.close()
#
#            for i in range(len(lines)):
#                while dst_dir in lines[i]:
#                    lines[i] = lines[i].replace(dst_dir, '')
#
#            la_file = open(la_file_name, 'w')
#            la_file.write('\n'.join(lines))
#            la_file.close()

    return ret

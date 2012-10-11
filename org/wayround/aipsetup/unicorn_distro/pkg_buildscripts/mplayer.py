#!/usr/bin/python

import os.path
import logging
import io
import subprocess

import org.wayround.utils.file
import org.wayround.utils.stream

import org.wayround.aipsetup.buildingsite
import org.wayround.aipsetup.build
import org.wayround.aipsetup.buildtools.autotools as autotools


def main(buildingsite, action=None):

    ret = 0

    r = org.wayround.aipsetup.build.build_script_wrap(
            buildingsite,
            ['configure', 'build', 'distribute'],
            action,
            "help"
            )

    if not isinstance(r, tuple):
        logging.error("Error")
        ret = r

    else:

        pkg_info, actions = r

        src_dir = org.wayround.aipsetup.buildingsite.getDIR_SOURCE(buildingsite)

        separate_build_dir = False

        source_configure_reldir = '.'

        # if 'extract' in actions:
        #     if os.path.isdir(src_dir):
        #         logging.info("cleaningup source dir")
        #         org.wayround.utils.file.cleanup_dir(src_dir)
        #     ret = autotools.extract_high(
        #         buildingsite,
        #         pkg_info['pkg_info']['basename'],
        #         unwrap_dir=True,
        #         rename_dir=False
        #         )

        lib_ass_f = io.StringIO()
        lib_ass_cflags = ''
        proc = subprocess.Popen(['pkg-config', '--cflags', 'libass'], stdout=subprocess.PIPE)

        stream = org.wayround.utils.stream.cat(proc.stdout, lib_ass_f, convert_to_str='utf-8', threaded=True)
        stream.start()
        stream.join()

        if proc.wait() != 0:
            logging.error("Error getting libass C flags")
            ret = 4
        
        if ret == 0:
            lib_ass_f.seek(0)
            lib_ass_cflags = lib_ass_f.readlines()[0].strip()
        lib_ass_f.close()

        lib_ass_f = io.StringIO()
        lib_ass_libs = ''
        
        proc = subprocess.Popen(['pkg-config', '--libs', 'libass'], stdout=subprocess.PIPE)

        stream = org.wayround.utils.stream.cat(proc.stdout, lib_ass_f, convert_to_str='utf-8', threaded=True)
        stream.start()
        stream.join()

        if proc.wait() != 0:
            logging.error("Error getting libass lib flags")
            ret = 4
        
        if ret == 0:
            lib_ass_f.seek(0)
            lib_ass_libs = lib_ass_f.readlines()[0].strip()
        lib_ass_f.close()
        

        if 'configure' in actions and ret == 0:
            ret = autotools.configure_high(
                buildingsite,
                options=[
                    '--enable-gui',
                    '--enable-radio',
                    '--enable-radio-capture',
                    '--enable-radio-v4l2', 
                    '--enable-tv', 
                    '--enable-tv-v4l2', 
                    '--enable-vcd', 
                    '--enable-freetype', 
                    '--enable-ass', 
                    '--enable-gif', 
                    '--enable-png', 
                    '--enable-mng', 
                    '--enable-jpeg', 
                    '--enable-real', 
                    '--enable-xvid-lavc', 
                    '--enable-x264-lavc', 
                    '--extra-cflags='+ lib_ass_cflags, 
                    '--extra-ldflags='+lib_ass_libs,
                    '--prefix=' + pkg_info['constitution']['paths']['usr'],
                    '--mandir=' + pkg_info['constitution']['paths']['man'],
                    # '--sysconfdir=' + pkg_info['constitution']['paths']['config'], 
                    # '--localstatedir=' + pkg_info['constitution']['paths']['var'],
                    # '--enable-shared',
                    # '--host=' + pkg_info['constitution']['host'],
                    # '--build=' + pkg_info['constitution']['build'],
                    # '--target=' + pkg_info['constitution']['target']
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
                arguments=['LDFLAGS='+lib_ass_libs],
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
                    'DESTDIR=' + (
                        org.wayround.aipsetup.buildingsite.getDIR_DESTDIR(
                            buildingsite
                            )
                        )
                    ],
                environment={},
                environment_mode='copy',
                use_separate_buildding_dir=separate_build_dir,
                source_configure_reldir=source_configure_reldir
                )

    return ret

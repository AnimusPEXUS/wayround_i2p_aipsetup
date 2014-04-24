
import glob
import logging
import os.path
import shutil
import subprocess

import org.wayround.aipsetup.build
import org.wayround.aipsetup.buildtools.autotools as autotools
import org.wayround.utils.file


def main(buildingsite, action=None):

    ret = 0

    r = org.wayround.aipsetup.build.build_script_wrap(
        buildingsite,
        ['extract', 'build', 'distribute', 'so', 'copy_so', 'fix_links'],
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
                arguments=[
                    'PREFIX=/usr',
                    'CFLAGS=-Wall -Winline -O2 -g '
                    '-D_FILE_OFFSET_BITS=64 -march=i486 -mtune=i486'
                    ],
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
                    'PREFIX=' + os.path.join(dst_dir, 'usr')
                    ],
                environment={},
                environment_mode='copy',
                use_separate_buildding_dir=separate_build_dir,
                source_configure_reldir=source_configure_reldir
                )

        if 'so' in actions and ret == 0:
            p = subprocess.Popen(
                [
                 'make',
                 '-f', 'Makefile-libbz2_so',
                 'CFLAGS=-Wall -Winline -O2 -g '
                 '-D_FILE_OFFSET_BITS=64 -march=i486 -mtune=i486'
                 ],
                cwd=src_dir
                )
            ret = p.wait()

        if 'copy_so' in actions and ret == 0:

            di = os.path.join(dst_dir, 'usr', 'lib')

            try:
                os.makedirs(di)
            except:
                logging.error("Error Creating {}".format(di))

            try:
                sos = glob.glob(src_dir + '/*.so.*')

                for i in sos:

                    base = os.path.basename(i)

                    j = os.path.join(src_dir, base)
                    j2 = os.path.join(di, base)

                    if os.path.isfile(j) and not os.path.islink(j):
                        shutil.copy(j, j2)

                    elif os.path.isfile(j) and os.path.islink(j):
                        lnk = os.readlink(j)
                        os.symlink(lnk, j2)

                    else:
                        raise Exception("Programming error")

            except:
                logging.exception("Error")
                ret = 2

        if 'fix_links' in actions and ret == 0:

            bin_dir = os.path.join(dst_dir, 'usr', 'bin')
            files = os.listdir(bin_dir)

            try:
                for i in files:

                    ff = os.path.join(bin_dir, i)

                    if os.path.islink(ff):

                        base = os.path.basename(os.readlink(ff))

                        if os.path.exists(ff):
                            os.unlink(ff)

                        os.symlink(base, ff)

            except:
                logging.exception("Error")
                ret = 3

    return ret

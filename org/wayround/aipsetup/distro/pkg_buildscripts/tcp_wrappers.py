
import logging
import os.path
import subprocess
import glob

import org.wayround.aipsetup.build
import org.wayround.aipsetup.buildtools.autotools as autotools
import org.wayround.utils.file


def main(buildingsite, action=None):

    ret = 0

    r = org.wayround.aipsetup.build.build_script_wrap(
        buildingsite,
        ['extract', 'patch', 'build', 'distribute'],
        action,
        "help"
        )

    if not isinstance(r, tuple):
        logging.error("Error")
        ret = r

    else:

        pkg_info, actions = r

        src_dir = org.wayround.aipsetup.build.getDIR_SOURCE(buildingsite)

        patch_dir = org.wayround.aipsetup.build.getDIR_PATCHES(buildingsite)

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

            patches = os.listdir(patch_dir)
            patches.sort()

            if len(patches) == 0:
                logging.error("Patches not supplied")
                ret = 3
            else:

                for i in patches:
                    p = subprocess.Popen(
                        ['patch', '-i', org.wayround.utils.path.join(patch_dir, i)],
                        cwd=src_dir
                        )
                    p.wait()

        if 'build' in actions and ret == 0:
            p = subprocess.Popen(
                ['make', 'linux'],
                cwd=src_dir
                )
            if p.wait() != 0:
                ret = 2


        if 'distribute' in actions and ret == 0:

            # make dirs

            for i in [
                'usr/lib',
                'usr/bin',
                'usr/share/man',
                'usr/include',
                ]:
                pp = org.wayround.utils.path.join(dst_dir, i)
                if not os.path.isdir(pp):
                    os.makedirs(pp)

            # shared

            shared_dir = org.wayround.utils.path.join(src_dir,'shared')

            shared = os.listdir(shared_dir)

            for i in shared:
                if i.startswith('libwrap'):
                    p = subprocess.Popen(
                        [
                            'cp',
                            org.wayround.utils.path.join(shared_dir, i),
                            org.wayround.utils.path.join(
                                dst_dir,
                                'usr/lib'
                            )
                        ]
                    )
                    if p.wait() != 0:
                        ret = 5

            # *.a
            
            for i in os.listdir(src_dir):
                if i.endswith('.a'):
                    p = subprocess.Popen(
                        [
                            'cp',
                            org.wayround.utils.path.join(src_dir, i),
                            org.wayround.utils.path.join(
                                dst_dir,
                                'usr/lib'
                            )
                        ]
                    )
                    if p.wait() != 0:
                        ret = 8

            # *.h

            for i in os.listdir(src_dir):
                if i.endswith('.h'):
                    p = subprocess.Popen(
                        [
                            'cp',
                            org.wayround.utils.path.join(src_dir, i),
                            org.wayround.utils.path.join(
                                dst_dir,
                                'usr/include'
                            )
                        ]
                    )
                    if p.wait() != 0:
                        ret = 8


            # executables

            for i in ['safe_finger', 'tcpd', 'tcpdchk', 'tcpdmatch', 'try-from']:
                p = subprocess.Popen(
                    ['cp',
                     org.wayround.utils.path.join(src_dir, i),
                     org.wayround.utils.path.join(dst_dir, 'usr/bin')
                    ]
                )
                if p.wait() != 0:
                    ret = 6


            # man pages

            for i in range(10):
                dd = org.wayround.utils.path.join(dst_dir, 'usr', 'share', 'man', 'man{}'.format(i))
                if not os.path.isdir(dd):
                    os.makedirs(dd)

                b = glob.glob(src_dir + '/*.{}'.format(i))

                for j in b:
                    p = subprocess.Popen(
                        ['cp',
                         org.wayround.utils.path.join(j),
                         org.wayround.utils.path.join(dd, os.path.basename(j))
                        ]
                    )
                    if p.wait() != 0:
                        ret = 7

    return ret

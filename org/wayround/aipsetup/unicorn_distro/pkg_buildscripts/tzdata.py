#!/usr/bin/python

import os.path
import logging
import subprocess
import shutil
import glob

import org.wayround.utils.file

import org.wayround.aipsetup.build
import org.wayround.aipsetup.build
import org.wayround.aipsetup.buildtools.autotools as autotools


def main(buildingsite, action=None):

    ret = 0

    r = org.wayround.aipsetup.build.build_script_wrap(
        buildingsite,
        # ['cleanup','extract', 'configure', 'build', 'distribute'],
        ['cleanup', 'extract', 'configure', 'distribute'],
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

        tar_dir = org.wayround.aipsetup.build.getDIR_TARBALL(buildingsite)

        separate_build_dir = False

        source_configure_reldir = '.'

        makefile = os.path.join(src_dir, 'Makefile')

        zoneinfo = os.path.join(dst_dir, 'usr', 'share', 'zoneinfo')
        zoneinfop = os.path.join(dst_dir, 'usr', 'share', 'zoneinfo', 'posix')
        zoneinfor = os.path.join(dst_dir, 'usr', 'share', 'zoneinfo', 'right')

        files = os.listdir(tar_dir)

        # tzcode=None
        tzdata = None

        for i in files:
            if i.startswith('tzdata'):
                tzdata = i
                break

        # for i in files:
        #     if i.startswith('tzcode'):
        #         tzcode=i
        #         break

        if tzdata == None:
            logging.error("tzdata missing in tarball dir")
            logging.error("It can be tacken from IANA site")

            ret = 100

        if 'cleanup'in actions and ret == 0:
            if os.path.isdir(src_dir):
                logging.info("cleaningup source dir")
                org.wayround.utils.file.cleanup_dir(src_dir)


        if 'extract' in actions and ret == 0:

            ret = autotools.extract_high(
                buildingsite,
                'tzdata',
                unwrap_dir=False,
                rename_dir=False,
                more_when_one_extracted_ok=True
                )

            logging.info("Extracted with code {}".format(ret))

        # if 'extract2' in actions and ret ==0:

        #     ret = autotools.extract_high(
        #         buildingsite,
        #         'tzcode',
        #         unwrap_dir=False,
        #         rename_dir=False,
        #         more_when_one_extracted_ok=True
        #         )

        #     logging.info("Extracted with code {}".format(ret))


        # if 'configure' in actions and ret == 0:

        #     try:
        #         f=open(makefile, 'r')
        #         txt = f.read()
        #         f.close()


        #         txtl = txt.splitlines()

        #         for i in range(len(txtl)):

        #             if txtl[i].startswith('TOPDIR='):
        #                 txtl[i] = 'TOPDIR={}\n'.format(os.path.join(dst_dir, 'usr'))

        #         f=open(makefile, 'w')
        #         f.write('\n'.join(txtl))
        #         f.close()
        #     except:
        #         logging.exception("Can't do some actions on Makefile")
        #         ret = 1
        #     else:
        #         ret = 0

        if 'configure' in actions and ret == 0:

            try:
                f = open(makefile, 'r')
                txt = f.read()
                f.close()



                txt += """
printtdata:
		@echo "$(TDATA)"
"""

                f = open(makefile, 'w')
                f.write(txt)
                f.close()
            except:
                logging.exception("Can't do some actions on Makefile")
                ret = 1
            else:
                ret = 0


        if 'distribute' in actions and ret == 0:

            os.makedirs(zoneinfo)
            os.makedirs(zoneinfop)
            os.makedirs(zoneinfor)

            zonefiles = []

            p = subprocess.Popen(['make', 'printtdata'], cwd=src_dir, stdout=subprocess.PIPE)
            r = p.wait()
            if r != 0:
                ret = r
            else:
                txt = str(p.stdout.read(), 'utf-8')
                zonefiles = txt.split(' ')
                zonefiles.sort()

                print("ZF: {}".format(', '.join(zonefiles)))

                for tz in zonefiles:

                    logging.info("Working with {} zone info".format(tz))

                    p = subprocess.Popen(
                        ['zic', '-L', '/dev/null', '-d', zoneinfo, '-y', 'sh yearistype.sh', tz ],
                        cwd=src_dir
                        )
                    p.wait()

                    p = subprocess.Popen(
                        ['zic', '-L', '/dev/null', '-d', zoneinfop, '-y', 'sh yearistype.sh', tz ],
                        cwd=src_dir
                        )
                    p.wait()

                    p = subprocess.Popen(
                        ['zic', '-L', 'leapseconds', '-d', zoneinfor, '-y', 'sh yearistype.sh', tz ],
                        cwd=src_dir
                        )
                    p.wait()

                for i in os.listdir(src_dir):
                    if i.endswith('.tab'):
                        shutil.copy(os.path.join(src_dir, i), os.path.join(zoneinfo, i))


    return ret

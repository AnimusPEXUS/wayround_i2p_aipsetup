
import logging
import os.path
import re
import shutil
import subprocess

import org.wayround.aipsetup.build
import org.wayround.aipsetup.buildtools.autotools as autotools
import org.wayround.utils.file


def main(buildingsite, action=None):

    ret = 0

    r = org.wayround.aipsetup.build.build_script_wrap(
        buildingsite,
        ['extract', 'make_gen', 'build', 'distribute'],
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

        if 'make_gen' in actions and ret == 0:

            new_make_filename = org.wayround.utils.path.join(
                src_dir,
                'pdftk',
                'Makefile.Lailalo'
                )

            file_list = os.listdir('/usr/share/java')

            ver = None
            for i in file_list:
                res = re.match(r'^libgcj-((\d+\.?)+).jar$', i)
                if res:
                    ver = res.group(1)
                    logging.info("Found jcg version {}".format(ver))

            if not ver:
                ret = 3
            else:
                gcj_version = ver

                new_make_filename_f = open(new_make_filename, 'w')

                new_make_filename_f.write("""\
# -*- Mode: Makefile -*-
# Makefile.Lailalo
# Copyright (c) 2013 WayRound.org
# based on Makefile.Slackware-13.1
#
# Visit: www.pdftk.com for pdftk information and articles
# Permalink: http://www.pdflabs.com/tools/pdftk-the-pdf-toolkit/
#
# Brief Instructions
#
#   Compile:             make -f Makefile.Lailalo
#   Install (as root):   make -f Makefile.Lailalo install
#   Uninstall:           make -f Makefile.Lailalo uninstall
#   Clean:               make -f Makefile.Lailalo clean
#


TOOLPATH=
export VERSUFF=-{gcj_version}
export CXX= $(TOOLPATH)g++
export GCJ= $(TOOLPATH)gcj
export GCJH= $(TOOLPATH)gcjh
export GJAR= $(TOOLPATH)gjar
export LIBGCJ= /usr/share/java/libgcj$(VERSUFF).jar
export AR= ar
export RM= rm
export ARFLAGS= rs
export RMFLAGS= -vf

export CPPFLAGS= -DPATH_DELIM=0x2f -DASK_ABOUT_WARNINGS=false \
-DUNBLOCK_SIGNALS -fdollars-in-identifiers
export CXXFLAGS= -Wall -Wextra -Weffc++ -O2
export GCJFLAGS= -Wall -fsource=1.3 -O2
export GCJHFLAGS= -force
export LDLIBS= -lgcj

include Makefile.Base
""".format(gcj_version=gcj_version)
                    )
                new_make_filename_f.close()

        if 'build' in actions and ret == 0:
            p = subprocess.Popen(
                ['make', '-f', 'Makefile.Lailalo'],
                cwd=org.wayround.utils.path.join(src_dir, 'pdftk')
                )
            ret = p.wait()

        if 'distribute' in actions and ret == 0:
            sbin = org.wayround.utils.path.join(src_dir, 'pdftk', 'pdftk')
            bin_dir = org.wayround.utils.path.join(dst_dir, 'usr', 'bin')

            try:
                os.makedirs(bin_dir)
            except:
                pass

            if not os.path.isdir(bin_dir):
                logging.error("Can't create dir: `{}'".format(bin_dir))
                ret = 22
            else:
                shutil.copy(
                    sbin, org.wayround.utils.path.join(bin_dir, 'pdftk')
                    )

            sman = org.wayround.utils.path.join(src_dir, 'pdftk.1')
            man = org.wayround.utils.path.join(
                dst_dir, 'usr', 'share', 'man', 'man1'
                )

            try:
                os.makedirs(man)
            except:
                pass

            if not os.path.isdir(man):
                logging.error("Can't create dir: `{}'".format(man))
                ret = 23
            else:
                shutil.copy(sman, org.wayround.utils.path.join(man, 'pdftk.1'))

    return ret

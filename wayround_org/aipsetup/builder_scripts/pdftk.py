
import re
import os.path
import shutil
import subprocess

import wayround_org.utils.path
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_actions(self):
        ret = super().define_actions()
        del(ret['autogen'])
        return ret

    def builder_action_configure(self, called_as, log):
        new_make_filename = wayround_org.utils.path.join(
            self.get_src_dir(),
            'pdftk',
            'Makefile.Lailalo'
            )

        file_list = os.listdir(
            wayround_org.utils.path.join(
                self.get_host_dir(),
                'share',
                'java'
                )
            )

        ver = None
        for i in file_list:
            res = re.match(r'^libgcj-((\d+\.?)+).jar$', i)
            if res:
                ver = res.group(1)
                log.info("Found jcg version {}".format(ver))

        if not ver:
            ret = 3
        else:
            gcj_version = ver

            new_make_filename_f = open(new_make_filename, 'w')

            # FIXME: paths need to be redone
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
export LIBGCJ= {prefix}/share/java/libgcj$(VERSUFF).jar
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
""".format(
                    gcj_version=gcj_version,
                    prefix=self.calculate_install_prefix()
                    )
                )
            new_make_filename_f.close()
        return 0

    def builder_action_build(self, called_as, log):
        p = subprocess.Popen(
            ['make', '-f', 'Makefile.Lailalo'],
            cwd=wayround_org.utils.path.join(self.get_src_dir(), 'pdftk'),
            stdout=log.stdout,
            stderr=log.stderr
            )
        ret = p.wait()
        return ret

    def builder_action_distribute(self, called_as, log):

        ret = 0

        sbin = wayround_org.utils.path.join(
            self.get_src_dir(),
            'pdftk',
            'pdftk'
            )
        bin_dir = wayround_org.utils.path.join(
            self.calculate_dst_install_prefix(), 'bin'
            )

        os.makedirs(bin_dir, exist_ok=True)

        if not os.path.isdir(bin_dir):
            log.error("Can't create dir: `{}'".format(bin_dir))
            ret = 22
        else:
            shutil.copy(
                sbin,
                wayround_org.utils.path.join(bin_dir, 'pdftk')
                )

        sman = wayround_org.utils.path.join(self.get_src_dir(), 'pdftk.1')
        man = wayround_org.utils.path.join(
            self.calculate_dst_install_prefix(), 'share', 'man', 'man1'
            )

        os.makedirs(man, exist_ok=True)

        if not os.path.isdir(man):
            log.error("Can't create dir: `{}'".format(man))
            ret = 23
        else:
            shutil.copy(sman, wayround_org.utils.path.join(man, 'pdftk.1'))
        return ret

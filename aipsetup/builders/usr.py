# -*- coding: utf-8 -*-

import glob

import aipsetup.build
import aipsetup.extractor
import aipsetup.tools.autotools


# aipsetup.tools.autotools.configure(
#     options=['--prefix=/usr', '--sysconfdir=/etc', '--localstatedir=/var', '--enable-shared', '--host=i486-pc-linux-gnu', '--build=i486-pc-linux-gnu'],
#     build_dir='.',
#     run_dir='.'
#     )

__file__ = os.path.abspath(__file__)
PPWD = os.path.dirname(__file__)

files = glob.glob(aipsetup.build.DIR_TARBALL + '/*')

if len(files) != 1:
    print("-e- There must be exactly one sorce tarball")

print("-i- found %(file)s, trying to extract..." % {'file': files[0]})

aipsetup.extractor.extract(files[0], aipsetup.build.DIR_SOURCE)

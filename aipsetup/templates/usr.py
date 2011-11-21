# -*- coding: utf-8 -*-

import aipsetup.sourceconfigure

aipsetup.sourceconfigure.at_configure(
    options=['--prefix=/usr', '--sysconfdir=/etc', '--localstatedir=/var', '--enable-shared', '--host=i486-pc-linux-gnu', '--build=i486-pc-linux-gnu'],
    build_dir='.',
    run_dir='.'
    )

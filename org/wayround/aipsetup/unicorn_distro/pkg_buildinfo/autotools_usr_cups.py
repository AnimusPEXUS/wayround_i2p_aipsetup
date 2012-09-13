#!/usr/bin/python
# -*- coding: utf-8 -*-

import org.wayround.aipsetup.buildinfo

def build_info():

    ret = org.wayround.aipsetup.buildinfo.load_buildinfo('autotools_usr')
    ret['autotools_distribute_opts']['DESTDIR_opt_name'] = 'BUILDROOT'
    ret['autotools_configure_opts']['separate_build_dir'] = False

    return ret

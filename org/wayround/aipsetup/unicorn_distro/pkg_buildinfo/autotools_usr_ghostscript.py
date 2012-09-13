#!/usr/bin/python
# -*- coding: utf-8 -*-

import org.wayround.aipsetup.buildinfo

def build_info():

    ret = org.wayround.aipsetup.buildinfo.load_buildinfo('autotools_usr')
    ret['build_tools']['build'] = 'autotools_ghostscript'
    ret['build_tools']['distribute'] = 'autotools_ghostscript'
    ret['autotools_configure_params']['with-x'] = 'yes'
    ret['autotools_configure_params']['with-install-cups'] = 'yes'

    ret['autotools_configure_opts']['separate_build_dir'] = False

    return ret

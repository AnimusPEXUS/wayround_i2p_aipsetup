#!/usr/bin/python
# -*- coding: utf-8 -*-

import org.wayround.aipsetup.buildscript

def build_script():

    ret = org.wayround.aipsetup.buildscript.load_buildscript('autotools_usr')
    ret['autotools_configure_params']['with-x'] = 'yes'
    ret['autotools_configure_params']['enable-xpdf-headers'] = 'yes'

#    ret['autotools_configure_opts']['separate_build_dir'] = False


    return ret

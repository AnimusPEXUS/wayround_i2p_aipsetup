#!/usr/bin/python
# -*- coding: utf-8 -*-

import org.wayround.aipsetup.buildscript

def build_script():

    ret = org.wayround.aipsetup.buildscript.load_buildscript('autotools_usr')
    ret['autotools_configure_params']['enable-kernel'] = '2.6.39.3'
    ret['autotools_configure_params']['enable-tls'] = 'yes'
    ret['autotools_configure_params']['with-elf'] = 'yes'
    ret['autotools_configure_params']['enable-multi-arch'] = 'yes'

#    ret['autotools_configure_opts']['separate_build_dir'] = False


    return ret

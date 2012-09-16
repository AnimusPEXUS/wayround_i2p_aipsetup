#!/usr/bin/python
# -*- coding: utf-8 -*-

import org.wayround.aipsetup.buildscript

def build_script():

    ret = org.wayround.aipsetup.buildscript.load_buildscript('autotools_usr')
    ret['autotools_configure_params']['enable-foomatic-rip-hplip-install'] = 'yes'
    ret['autotools_configure_params']['enable-hpijs-install'] = 'yes'
    ret['autotools_configure_params']['enable-hpcups-install'] = 'yes'
    ret['autotools_configure_params']['enable-gui-build'] = 'yes'
    ret['autotools_configure_params']['enable-foomatic-ppd-install'] = 'yes'
    ret['autotools_configure_params']['enable-foomatic-drv-install'] = 'yes'
    ret['autotools_configure_params']['enable-cups-drv-install'] = 'yes'
    ret['autotools_configure_params']['enable-cups-ppd-install'] = 'yes'

    ret['autotools_configure_opts']['separate_build_dir'] = False


    return ret
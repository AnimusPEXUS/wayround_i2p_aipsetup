#!/usr/bin/python
# -*- coding: utf-8 -*-

import org.wayround.aipsetup.buildscript

def build_script():

    ret = org.wayround.aipsetup.buildscript.load_buildscript('autotools_usr')
    ret['autotools_configure_params']['enable-languages'] = 'all,go,objc,obj-c++'
    ret['autotools_configure_params']['enable-bootstrap'] = 'yes'
    ret['autotools_configure_params']['enable-tls'] = 'yes'
    ret['autotools_configure_params']['enable-nls'] = 'yes'
    ret['autotools_configure_params']['enable-threads'] = 'posix'
    ret['autotools_configure_params']['enable-multiarch'] = 'yes'
#    ret['autotools_configure_params']['with-cpu'] = 'generic'
#    ret['autotools_configure_params']['with-arch'] = 'generic'
#    ret['autotools_configure_params']['with-tune'] = 'generic'
    ret['autotools_configure_params']['enable-checking'] = 'release'
    ret['autotools_configure_params']['with-gmp'] = '/usr'
    ret['autotools_configure_params']['with-mpfr'] = '/usr'
    ret['autotools_configure_params']['enable-targets'] = 'all'

    ret['autotools_configure_opts']['separate_build_dir'] = False


    return ret

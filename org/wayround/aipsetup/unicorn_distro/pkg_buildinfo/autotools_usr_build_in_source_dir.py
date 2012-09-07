#!/usr/bin/python
# -*- coding: utf-8 -*-

import org.wayround.aipsetup.buildinfo
import logging

def build_info():

    ret = org.wayround.aipsetup.buildinfo.load_buildinfo('autotools_usr')
    ret['autotools_configure_opts']['separate_build_dir'] = False

    logging.info("configured to build in source dir")


    return ret

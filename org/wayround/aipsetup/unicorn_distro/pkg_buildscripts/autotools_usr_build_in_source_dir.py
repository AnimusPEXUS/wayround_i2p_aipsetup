#!/usr/bin/python
# -*- coding: utf-8 -*-

import org.wayround.aipsetup.buildscript
import logging

def build_script():

    ret = org.wayround.aipsetup.buildscript.load_buildscript('autotools_usr')
    ret['autotools_configure_opts']['separate_build_dir'] = False

    logging.info("configured to build in source dir")


    return ret

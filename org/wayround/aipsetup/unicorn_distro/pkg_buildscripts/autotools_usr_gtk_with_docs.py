#!/usr/bin/python
# -*- coding: utf-8 -*-

import org.wayround.aipsetup.buildscript
import logging

def build_script():

    ret = org.wayround.aipsetup.buildscript.load_buildscript('autotools_usr')
    ret['autotools_configure_params']['enable-gtk-doc'] = 'yes'

    logging.info("configured to build documentation for Gtk-3.0")

    return ret

#!/usr/bin/python
# -*- coding: utf-8 -*-

import org.wayround.aipsetup.buildinfo
import logging

def build_info():

    ret = org.wayround.aipsetup.buildinfo.load_buildinfo('autotools_usr')
    ret['autotools_configure_params']['enable-gtk-doc'] = 'yes'

    logging.info("configured to build documentation for Gtk-3.0")

    return ret

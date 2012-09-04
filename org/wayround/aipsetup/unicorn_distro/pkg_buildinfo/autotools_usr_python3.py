#!/usr/bin/python
# -*- coding: utf-8 -*-

import org.wayround.aipsetup.constitution
import org.wayround.aipsetup.buildinfo
import logging

def build_info():

    ret = org.wayround.aipsetup.buildinfo.load_buildinfo('autotools_usr')

    logging.info("configured to use python3")

    ret['autotools_configure_envs']['PYTHON'] = (
        '/usr/bin/python3'
        )

    return ret

#!/usr/bin/python
# -*- coding: utf-8 -*-

import org.wayround.aipsetup.constitution
import org.wayround.aipsetup.buildscript
import logging

def build_script():

    ret = org.wayround.aipsetup.buildscript.load_buildscript('autotools_usr')

    logging.info("configured to use python3")

    ret['autotools_configure_envs']['PYTHON'] = (
        '/usr/bin/python3'
        )

    return ret

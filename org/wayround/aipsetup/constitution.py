
"""
Actions related to constitution file
"""

import logging
import re

import org.wayround.utils.edit

import org.wayround.aipsetup.config


def exported_commands():
    return {
        'edit': constitution_edit,
        'cat': constitution_cat
        }

def commands_order():
    return ['edit', 'cat']

def constitution_edit(opts, args):
    """
    Edit constitution.py file in UNICORN directory
    """
    org.wayround.utils.edit.edit_file_direct(
        org.wayround.aipsetup.config.config['constitution'],
        org.wayround.aipsetup.config.config['editor']
        )

    return 0


def constitution_cat(opts, args):
    """
    cat contents of constitution.py file
    """
    try:
        f = open(org.wayround.aipsetup.config.config['constitution'], 'r')
    except:
        logging.exception(
            "Can't open `{}'".format(
                org.wayround.aipsetup.config.config['constitution']
                )
            )
    else:

        try:
            txt = f.read()
        finally:
            f.close()

    print(txt)
    return 0


def read_constitution():

    ret = None

    try:
        f = open(org.wayround.aipsetup.config.config['constitution'])
    except:
        logging.exception("Can't read constitution `{}'".format(org.wayround.aipsetup.config.config['constitution']))
        ret = None
    else:
        try:
            t = f.read()
            try:
                constitution = eval(t, {}, {})
            except:
                logging.exception("Error loading constitution script")
                ret = None
            else:
                ret = constitution
        finally:
            f.close()

    return ret

def parse_triplet(string):
    ret = None
    a = re.match(r'(.*?)-(.*?)-(.*)', string)
    if a:
        ret = (a.group(1), a.group(2), a.group(3))
    return ret

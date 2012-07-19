
"""
Actions related to constitution file
"""

import logging

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
    f = open(org.wayround.aipsetup.config.config['constitution'], 'r')
    txt = f.read()
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
        t = f.read()
        try:
            constitution = eval(t, {}, {})
        except:
            logging.exception("Error loading constitution script")
            ret = None
        else:
            ret = constitution

    return ret

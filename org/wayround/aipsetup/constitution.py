
import logging

import org.wayround.utils.edit

import org.wayround.aipsetup.config

def help_text():
    return """\
{aipsetup} {command} command

    edit   edit constitution file

    view   view constitution file
"""

def router(opts, args):

    ret = org.wayround.aipsetup.router.router(
        opts, args, commands={
            'edit': edit,
            'cat': cat
            }
        )

    return ret


def edit(opts, args):
    org.wayround.utils.edit.edit_file_direct(
        org.wayround.aipsetup.config.config['constitution'],
        org.wayround.aipsetup.config.config['editor']
        )

    return 0


def cat(opts, args):
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
            logging.exception("-e- Error loading constitution script")
            ret = None
        else:
            ret = constitution

    return ret

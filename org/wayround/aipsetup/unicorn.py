
"""
Manipulate UNICORN installation base dir
"""

import os.path
import logging

import org.wayround.utils.file

import org.wayround.aipsetup.config

def exported_commands():
    return {
        'install': unicorn_install
        }

def commands_order():
    return [
        'install'
        ]

def cli_name():
    return 'unicorn'


def unicorn_install(opts, args):
    """
    Install new (initial) UNICORN distribution into selected directory.

    Directory pointed by unicorn_root in aipsetup.conf will be used.

    Directory MUST BE empty!
    """

    ret = 0

    dst_unicorn_dir = org.wayround.aipsetup.config.config['unicorn_root']

    #    if len(args) > 0:
    #        dst_unicorn_dir = args[0]

    dst_unicorn_dir = os.path.abspath(dst_unicorn_dir)

    if org.wayround.utils.file.create_if_not_exists_dir(dst_unicorn_dir) != 0:
        logging.error("Can't create dir `{}'".format(dst_unicorn_dir))
        ret = 1
    else:
        if not org.wayround.utils.file.isdirempty(dst_unicorn_dir):
            logging.error("Dir `{}' isn't empty".format(dst_unicorn_dir))
            ret = 2
        else:
            src_unicorn_dir = source_unicorn_dir()
            if org.wayround.utils.file.copytree(
                src_unicorn_dir, dst_unicorn_dir,
                overwrite_files=False,
                clear_before_copy=False,
                dst_must_be_empty=False
                ) != 0:
                logging.error("Error while copying UNICORN files")
                ret = 3
            else:
                logging.info("UNICORN distro installation completed")

    return ret


def source_unicorn_dir():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), 'unicorn_distro'))

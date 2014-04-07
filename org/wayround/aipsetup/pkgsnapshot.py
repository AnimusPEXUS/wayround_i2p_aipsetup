
"""
Installation environment snapshots
"""

import json
import logging
import os
import re

import org.wayround.aipsetup.config
import org.wayround.aipsetup.package
import org.wayround.aipsetup.clean

import org.wayround.utils.time


#def exported_commands():
#    return {
#        'list':pkgsnapshots_print_list,
#        'create':pkgsnapshots_create
#        }
#
#def commands_order():
#    return [
#        'list',
#        'create'
#        ]
#
#def cli_name():
#    return 'snap'


def pkgsnapshots_print_list(opts, args):

    lst = list_snapshots()

    lst.sort(reverse=True)

    for i in lst:
        print(i)

    return


def pkgsnapshots_create(opts, args):

    create_snapshot()


def create_snapshot():

    ret = 0

    name = org.wayround.utils.time.currenttime_stamp()

    snapshots_dir = org.wayround.aipsetup.config.config['snapshots']

    if not os.path.isdir(snapshots_dir):
        os.makedirs(snapshots_dir)

    content = org.wayround.aipsetup.package.list_installed_packages_and_asps()

    if org.wayround.aipsetup.clean.check_list_of_installed_packages_and_asps(
        content
        ) != 0:
        logging.error("Snapshot with errors can't be created")
        ret = 1

    else:

        full_file_name = os.path.join(snapshots_dir, name + '.json')

        f = open(full_file_name, 'w')

        f.write(json.dumps(content, indent=4))

        f.close()

    return ret


def list_snapshots():

    snapshots_dir = org.wayround.aipsetup.config.config['snapshots']

    if not os.path.isdir(snapshots_dir):
        os.makedirs(snapshots_dir)

    lst = []
    _lst = os.listdir(snapshots_dir)

    for i in _lst:

        re_m = re.match(
            org.wayround.utils.time.TIMESTAMP_RE_PATTERN + '\.json',
            i
            )

        if not re_m:
            logging.error("Wrong snapshot name `{}'".format(i))

        else:
            lst.append(i)

    return lst

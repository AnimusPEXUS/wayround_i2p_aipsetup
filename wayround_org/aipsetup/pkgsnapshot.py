
"""
Installation environment snapshots
"""

import json
import logging
import os
import re

import wayround_org.aipsetup.config
import wayround_org.aipsetup.package
import wayround_org.aipsetup.clean

import wayround_org.utils.time


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

    name = wayround_org.utils.time.currenttime_stamp()

    snapshots_dir = wayround_org.aipsetup.config.config['snapshots']

    if not os.path.isdir(snapshots_dir):
        os.makedirs(snapshots_dir)

    content = wayround_org.aipsetup.package.list_installed_packages_and_asps()

    if wayround_org.aipsetup.clean.check_list_of_installed_packages_and_asps(
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

    snapshots_dir = wayround_org.aipsetup.config.config['snapshots']

    if not os.path.isdir(snapshots_dir):
        os.makedirs(snapshots_dir)

    lst = []
    _lst = os.listdir(snapshots_dir)

    for i in _lst:

        re_m = re.match(
            wayround_org.utils.time.TIMESTAMP_RE_PATTERN + '\.json',
            i
            )

        if not re_m:
            logging.error("Wrong snapshot name `{}'".format(i))

        else:
            lst.append(i)

    return lst

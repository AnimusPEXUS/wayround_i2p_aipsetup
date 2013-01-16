AIPSETUP_VERSION = '3.0'


AIPSETUP_CLI_MODULE_LIST = [
    'info',
    'buildscript',
    'constitution',

    'buildingsite',
    'build',
    'pack',
    'package',
    'pkgsnapshot',
    'server',
    'client',
    'repoman',

    'name',
    'docbook',
    'sysupdates',

    'config',
    'unicorn'
    ]
"""
modules able to be accessed from CLI
"""

AIPSETUP_CLI_MODULE_LIST_UNFUSED = [
    'config',
    ]
"""
modules allowed to be accessed from CLI without
proper aipsetup.conf
"""

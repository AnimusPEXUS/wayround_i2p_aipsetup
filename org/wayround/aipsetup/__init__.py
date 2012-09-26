AIPSETUP_VERSION = '3.0'

# modules allowed to be accessed from CLI (only if aipsetup.conf setup properly)
AIPSETUP_CLI_MODULE_LIST = [
    'info',
    'buildscript',
    'constitution',

    'buildingsite',
    'build',
    'pack',
    'package',
    'server',
    'client',
    'repoman',

    'name',
    'docbook',
    'sysupdates',

    'config',
    'unicorn'
    ]

# modules allowed to be accessed from CLI without 
# proper aipsetup.conf
AIPSETUP_CLI_MODULE_LIST_UNFUSED = [
    'config',
    ]

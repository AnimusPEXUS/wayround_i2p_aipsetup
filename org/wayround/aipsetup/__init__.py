AIPSETUP_VERSION = '3.0'

AIPSETUP_MODULES_LIST = frozenset(
    [
    'info',
    'buildscript',
    'constitution',

    'buildingsite',
    'build',
    'pack',
    'package',
    'server',
    'client',
    'pkgindex',

    'name',
    'docbook',
    'sysupdates',

    'config',
    'unicorn'
     ]
    )

AIPSETUP_MODULES_LIST_FUSED = AIPSETUP_MODULES_LIST - set(['config'])

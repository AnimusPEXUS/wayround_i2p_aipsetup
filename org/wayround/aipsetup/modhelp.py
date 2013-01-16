
"""
This module is used by :mod:`help <org.wayround.aipsetup.help>` module and other
modules, which need to list or help with other modules
"""

import logging

import org.wayround.aipsetup

class HelpModuleImportErrors(Exception): pass

def modules_tuple_list():
    """
    Return list of tubles describing modules.

    Each tuple in list have next structure:

    ==================== ======================================================
    accessor             meaning
    ==================== ======================================================
    t[0]                 short_name
    t[1]                 dict
    t[1]['name']         full module name ({} from 
                         'org.wayround.aipsetup.{}.cli_name')
    t[1]['short_name']   result of org.wayround.aipsetup.{}.cli_name() call
    t[1]['module']       module object
    ==================== ======================================================

    """

    ret = []

    import_errors = False


    for i in org.wayround.aipsetup.AIPSETUP_CLI_MODULE_LIST:
        m = 'org.wayround.aipsetup.' + i
        try:
            exec("import {}".format(m))
        except:
            logging.exception("Can't import module {}".format(m))
            import_errors = True

    if import_errors:
        raise HelpModuleImportErrors("Could not load some of the modules. See above.")

    for i in list(org.wayround.aipsetup.AIPSETUP_CLI_MODULE_LIST):
        try:
            short_name = eval('org.wayround.aipsetup.{}.cli_name()'.format(i))
        except:
            logging.error("Couldn't call org.wayround.aipsetup.{}.cli_name()".format(i))
            raise
        else:
            ret.append(
                (
                    short_name,
                    dict(
                        name=i,
                        short_name=short_name,
                        module=eval('org.wayround.aipsetup.{}'.format(i))
                        )
                    )
                )

    return ret

def modules_dict():
    """
    Turn tuple list returned by :func:`modules_tuple_list` to dict
    """
    return dict(modules_tuple_list())

def short_name_to_long(name):
    """
    Convert short module name to normal module name using :func:`modules_dict`
    """
    ret = None
    d = modules_dict()
    if name in d:
        ret = d[name]['name']
    return ret

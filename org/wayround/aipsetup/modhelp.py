
import logging

import org.wayround.aipsetup

class HelpModuleImportErrors(Exception): pass

def modules_tuple_list():

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
            name = eval('org.wayround.aipsetup.{}.cli_name()'.format(i))
        except:
            logging.error("Couldn't call org.wayround.aipsetup.{}.cli_name()".format(i))
            raise
        else:
            ret.append(
                (
                    name,
                    dict(
                        name=i,
                        short_name=name,
                        module=eval('org.wayround.aipsetup.{}'.format(i))
                        )
                    )
                )

    return ret

def modules_dict():
    return dict(modules_tuple_list())

def short_name_to_long(name):
    ret = None
    d = modules_dict()
    if name in d:
        ret = d[name]['name']
    return ret

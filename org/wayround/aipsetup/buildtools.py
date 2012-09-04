
import os.path
import glob
import logging
import inspect

import org.wayround.aipsetup.config

# TODO: May be command exporting needed. Not decided yet.

def list_build_tools():

    tools_dir = os.path.abspath(org.wayround.aipsetup.config.config['buildtools'])

    files = glob.glob(tools_dir + os.path.sep + '*.py')

    without_extensions = []
    for i in files:
        without_extensions.append(os.path.basename(i)[:-3])

    without_extensions.sort()

    return without_extensions

def get_tool(toolname):
    tools_dir = os.path.abspath(org.wayround.aipsetup.config.config['buildtools'])

    ret = None

    g = {}
    l = g

    filename = tools_dir + os.path.sep + toolname

    try:
        f = open(filename + '.py', 'r')
    except:
        logging.exception("Can't open `{}'".format(filename))
        ret = 1
        raise
    else:
        try:
            module_text = f.read()
            try:
                exec(module_text, g, l)
            except:
                logging.exception("Can't exec code in `{}'".format(filename))
                ret = 2
                raise
            else:
                ret = g
        finally:
            f.close()

    return ret

def get_tool_functions(toolname):

    ret = None

    g = get_tool(toolname)

    if (not isinstance(g, dict)
        or not 'export_functions' in g
        or not inspect.isfunction(g['export_functions'])
        ):
        logging.error(
            "No function `export_functions()' in tool `{}'".format(
                toolname
                )
            )
        ret = 1
    else:
        ret = g['export_functions']()

    return ret

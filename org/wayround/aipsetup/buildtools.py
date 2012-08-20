
import os.path
import glob
import logging

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

def get_tool_functions(toolname):

    tools_dir = os.path.abspath(org.wayround.aipsetup.config.config['buildtools'])

    g = {}
    l = {}

    filename = tools_dir + os.path.sep + toolname

    try:
        f = open(filename + '.py', 'r')
    except:
        logging.exception("Can't open `{}'".format(filename))
        raise
    else:
        try:
            module_text = f.read()
            module = exec(module_text, g, l)
        finally:
            f.close()

    return module.export_functions()


import os.path
import glob
import logging

import org.wayround.aipsetup.config


def list_build_tools():

    tools_dir = os.path.abspath(org.wayround.aipsetup.config.config['buildtools'])

    files = glob.glob(tools_dir + '/' + '*.py')

    without_extensions = []
    for i in files:
        without_extensions.append(os.path.basename(i)[:-3])

    without_extensions.sort()

    return without_extensions

def get_tool_functions(toolname):

    tools_dir = os.path.abspath(org.wayround.aipsetup.config.config['buildtools'])

    g = {}
    l = {}

    fn = tools_dir + '/' + toolname

    try:
        f = open(fn + '.py', 'r')
    except:
        logging.exception("Can't open `{}'".format(fn))
        raise
    else:
        try:
            module_text = f.read()
            module = exec(module_text, g, l)
        finally:
            f.close()

    return module.export_functions()

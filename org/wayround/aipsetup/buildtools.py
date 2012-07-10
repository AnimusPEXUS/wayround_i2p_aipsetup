
import os.path
import glob

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

    f = open(tools_dir + '/' + toolname + '.py', 'r')
    module_text = f.read()
    f.close()
    module = exec(module_text, g, l)

    return module.export_functions()

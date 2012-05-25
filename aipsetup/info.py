#!/usr/bin/python2.6
# -*- coding: utf-8 -*-

import os.path
import os
import copy
import glob
import sys

import lxml
import lxml.etree

import aipsetup.name
import aipsetup.version
import aipsetup.utils

from mako.template import Template
from mako import exceptions

SAMPLE_PACKAGE_INFO_STRUCTURE = dict(
    # not required, but can be usefull
    homepage="http://example.net",
    # description
    description="write something here, please",
    # this can be used for finding newer software versions (url list)
    sources=[],
    # url list
    mirrors = [],
    # 'standard', 'local' or other package name
    pkg_name_type = 'standard',
    # string list
    tags = [],
    # string
    buildinfo = ''
    )

pkg_info_file_template = Template(text="""\
<package>

  <!-- This file is generated by aipsetup -->

  <!-- name type can be 'standard', 'local' or other package name -->
  <nametype value="${ pkg_name_type | x}" />


  <description>${ description | x}</description>
  <homepage url="${ homepage | x}" />

  % if len(sources) == 0:
  <!-- Use <source url="" /> constructions for listing
       possible sources -->
  % endif
  % for i in sources:
  <source url="${ i | x}" />
  % endfor

  % if len(mirrors) == 0:
  <!-- Use <mirror url="" /> constructions for listing
       possible mirrors -->
  % endif
  % for i in mirrors:
  <mirror url="${ i | x}" />
  % endfor

  % if len(tags) == 0:
  <!-- Use <tag name="" /> constructions for listing
       tags -->
  % endif
  % for i in tags:
  <tag name="${ i | x}" />
  % endfor

  <buildinfo value="${ buildinfo | x }" />

</package>
""")

def _find_latest(tree, tag, field):
    y = None
    x = tree.findall(tag)
    if len(x) > 0:
        y = x[-1].get(field)
    return y

def _find_list(tree, tag, field):
    y = []
    x = tree.findall(tag)
    lx = len(x)
    for i in range(lx):
        z = x[i].get(field)
        if isinstance(z, basestring):
            y.append(z)
    return y

def print_help():
    print """\
aipsetup info command

   mass_info_fix  applayes fixes to info files

"""


def router(opts, args, config):

    ret = 0

    args_l = len(args)

    if args_l == 0:
        print "-e- command not given"
        ret = 1
    else:

        if args[0] == 'help':
            print_help()
            ret = 0

        elif args[0] == 'mass_info_fix':

            mass_info_fix(config)

        elif args[0] == 'list':

            mask = '*'

            if args_l > 2:
                print '-e- Too many parameters'
            else:

                if args_l > 1:
                    mask = args[1]

                utils.list_files(config, mask, 'info')


        elif args[0] == 'edit':

            if args_l != 2:
                print "-e- builder to edit not specified"
            else:
                utils.edit_file(config, args[1], 'info')

        elif args[0] == 'copy':

            if args_l != 3:
                print "-e- wrong parameters count"
            else:

                utils.copy_file(config, args[1], args[2], 'info')

        else:
            print "-e- wrong command"
            ret = 1

    return ret

def is_dicts_equal(d1, d2):

    ret = True

    for i in ['pkg_name_type', 'buildinfo',
              'homepage', 'description']:
        if d1[i] != d2[i]:
            ret = False
            break

    if ret:
        for i in ['sources', 'mirrors', 'tags']:

            if ret:
                for each in d1[i]:
                    if not each in d2[i]:
                        ret = False
                        break

            if ret:
                for each in d2[i]:
                    if not each in d1[i]:
                        ret = False
                        break

            if not ret:
                break

    return ret

def read_from_file(name):
    ret = None

    txt = ''
    tree = None

    try:
        f = open(aipsetup.utils.deunicodify(name), 'r')
        txt = f.read()
        f.close()
    except:
        print "-e- Can't open file %(name)s" % {
            'name': name
            }
        aipsetup.utils.print_exception_info(sys.exc_info())
        

    else:
        try:
            tree = lxml.etree.fromstring(txt)
        except:
            print "-e- Can't parse file %(name)s" % {
                'name': name
                }
            aipsetup.utils.print_exception_info(sys.exc_info())
            ret = 2
        else:
            ret = copy.copy(SAMPLE_PACKAGE_INFO_STRUCTURE)


            for i in ['buildinfo']:
                x = _find_latest(tree, i, 'value')
                if x != None:
                    ret[i] = x

            x = _find_latest(tree, 'nametype', 'value')
            if x != None:
                ret['pkg_name_type'] = x

            x = _find_latest(tree, 'homepage', 'url')
            if x != None:
                ret['homepage'] = x

            x = tree.findall('description')
            if len(x) > 0:
                ret['description'] = x[-1].text

            ret['sources'] = _find_list(tree, 'source', 'url')

            ret['mirrors'] = _find_list(tree, 'mirror', 'url')

            ret['tags'] = _find_list(tree, 'tag', 'name')
            ret['tags'].sort()

    return ret

def write_to_file(name, struct):

    ret = 0

    struct['tags'].sort()

    txt = pkg_info_file_template.render(
        pkg_name_type = struct['pkg_name_type'],
        description   = struct['description'],
        homepage      = struct['homepage'],
        sources       = struct['sources'],
        mirrors       = struct['mirrors'],
        tags          = struct['tags'],
        buildinfo     = struct['buildinfo']
        )

    try:
        f = open(aipsetup.utils.deunicodify(name), 'w')
        f.write(txt)
        f.close()
    except:
        print "-e- Can't rewrite file %(name)s" % {
            'name': name
            }
        aipsetup.utils.print_exception_info(sys.exc_info())
        ret = 1

    return ret

def info_fixes(dicti, name):

    if dicti['pkg_name_type'] == 'standard':

        pass

def mass_info_fix(config):

    lst = aipsetup.utils.unicodify(
        glob.glob(os.path.join(config['info'], '*.xml'))
        )


    for i in lst:

        name = os.path.basename(i)[:-4]

        dicti = read_from_file(i)

        info_fixes(dicti, name)

        write_to_file(i, dicti)

    print "-i- processed %(n)d files" % {
        'n': len(lst)
        }

    return
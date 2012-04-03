#!/usr/bin/python2.6
# -*- coding: utf-8 -*-

import os.path
import os
import copy

import lxml
import lxml.etree

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
    #
    # TODO: correct re
    regexp = 'name-(\d)*\.tar.(xz|gz|bz2|lzma)',
    # string list
    tags = [],
    # string
    builder = ''
    )

pkg_info_file_template = """\
<package>

  <!-- This file is generated by aipsetup -->

  <!-- name type can be 'standard', 'local' or other package name -->
  <nametype value="${ pkg_name_type | x}" />
  <regexp value="${ regexp | x}" />

  <description>${ description | x}</description>
  <homepage url="${ homepage | x}" />

  <!-- Use <source url="" /> constructions for listing
       possible sources -->
  % for i in sources:
  <source url="${ i | x}" />
  % endfor

  <!-- Use <mirror url="" /> constructions for listing
       possible mirrors -->
  % for i in mirrors:
  <mirror url="${ i | x}" />
  % endfor

  <!-- Use <tag name="" /> constructions for listing
       tags -->
  % for i in tags:
  <tag name="${ i | x}" />
  % endfor

  <builder value="${ builder | x }" />

</package>
"""

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

def is_dicts_equal(d1, d2):

    ret = True

    for i in ['pkg_name_type',
              'regexp', 'builder', 'homepage', 'description']:
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
        f = open(name, 'r')
        txt = f.read()
        f.close()
    except:
        ret = 1

    else:
        try:
            tree = lxml.etree.fromstring(txt)
        except:
            ret = 2
        else:
            ret = copy.copy(SAMPLE_PACKAGE_INFO_STRUCTURE)


            for i in ['regexp', 'builder']:
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

    txt = Template(text=pkg_info_file_template).render(
        pkg_name_type = struct['pkg_name_type'],
        regexp = struct['regexp'],
        description = struct['description'],
        homepage = struct['homepage'],
        sources = struct['sources'],
        mirrors = struct['mirrors'],
        tags = struct['tags'],
        builder = struct['builder']
        )

    try:
        f = open(name, 'w')
        f.write(txt)
        f.close()
    except:
        ret = 1

    return ret

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import os.path
import traceback
import sys
import re
import xml.sax.saxutils

import cherrypy

import aipsetup.getopt2
import aipsetup.utils
import aipsetup.pkgindex


from mako.template import Template
from mako import exceptions

def edefault(status, message, traceback, version):

    return "%(status)s: %(message)s" % {
        'message': xml.sax.saxutils.escape(message),
        'status': str(status)
        }

def print_help():
    print """\
aipsetup server command

   index_uht

      create all required indexes for UHT project

   start

      all settings taken from aipsetup.conf

"""

def router(opts, args, config):

    ret = 0

    if len(args) == 0:
        print "-e- not enough parameters"
        ret = 1
    else:

        if args[0] == 'help':
            print_help()
            ret = 0

        elif args[0] == 'index_uht':

            index_uht(config)

        elif args[0] == 'start':

            start_host(config)

        else:
            print "-e- wrong command"
            ret = 1

    return ret

def index_uht(config):
    index_directory(config['source'],
                    config['source_index'],
                    ['.tar.gz', '.tar.bz2', '.zip',
                     '.7z', '.tgz', '.tar.xz', '.tar.lzma',
                     '.tbz2'])
    index_directory(config['repository'],
                    config['repository_index'],
                    ['.asp'])




def _index_directory(f, root_dir, root_dirl, acceptable_endings=None):

    files = os.listdir(root_dir)
    files.sort()

    isfiles = 0

    for each in files:
        if each in ['.', '..']:
            continue

        full_path = os.path.join(root_dir, each)

        if os.path.islink(full_path):
            continue

        if not each[0] == '.' and os.path.isdir(full_path):
            _index_directory(f, full_path, root_dirl, acceptable_endings)

        elif not each[0] == '.' and os.path.isfile(full_path):

            if isinstance(acceptable_endings, list):

                match_found = False

                for i in acceptable_endings:
                    if each.endswith(i):
                        match_found = True
                        break

                if not match_found:
                    continue


            p = full_path[root_dirl:]
            f.write('%(name)s\n' % {
                    'name': p
                    })


def index_directory(dir_name, outputfilename='index.txt',
                    acceptable_endings=None):

    dir_name = os.path.abspath(dir_name)
    dir_namel = len(dir_name)

    print "-i- indexing %(dir)s..." % {'dir': dir_name}

    f=open(outputfilename, 'w')

    _index_directory(f, dir_name, dir_namel, acceptable_endings)

    f.close()

    return 0

class Index:

    def __init__(self, config, templates):

        self.config = config
        self.templates = templates
        self.pdb = aipsetup.pkgindex.PackageDatabase(self.config)

        self.index_reloading = False
        self.index_indexing = False
        self.index_error = True

        self.indexes = {
            'repository': [],
            'source': []
            }

        self.reload_indexes()


    def reload_indexes(self):

        print "-i- loading indexes"

        if not self.index_reloading:

            self.index_reloading = True

            indexing_errors = False

            for i in ['repository',
                      'source']:
                f = None
                try:
                    f = open(self.config['%(name)s_index' % {'name': i}],
                             'r')
                except:
                    indexing_errors = True
                else:
                    lst = f.readlines()
                    f.close()

                    self.indexes[i] = []

                    for j in lst:
                        self.indexes[i].append(j.strip())

                    self.indexes[i].sort()

            if indexing_errors:
                self.index_error = True
            else:
                self.index_error = False

            self.index_reloading = False

    def check_index(self):
        if self.index_reloading:
            raise cherrypy.HTTPError(503, "Reloading Indexes. Retry later!")
        elif self.index_indexing:
            raise cherrypy.HTTPError(503, "Recreating Indexes. Retry later!")
        elif self.index_error:
            raise cherrypy.HTTPError(500, "Index Error")

    def auth_user(self):

        users = {'admin': self.config['server_password']}

        # if not cherrypy.lib.auth.check_auth(users, realm='UHT_admin'):

        cherrypy.lib.auth.digest_auth(
            realm = 'UHT_admin',
            users = users,
            debug = True
            )

    def control(self, action=None):

        self.check_index()

        self.auth_user()

        if not action in [None, 'reload', 'reindex']:
            raise cherrypy.HTTPError(400, "Wrong parameter")

        if action == 'reload':
            self.reload_indexes()

        if action == 'reindex':
            self.index_indexing = True

            index_uht(self.config)

            self.reload_indexes()
            self.index_indexing = False


        control = self.templates['control'].render()

        html = self.templates['html'].render(
            title = 'UHT Server - Index Control',
            body = control
            )

        return html

    control.exposed = True

    def index(self, mode=None):

        self.check_index()

        index = self.templates['index'].render(
            )

        html = self.templates['html'].render(
            title = 'UHT Server - Welcome!',
            body = index
            )

        return html

    index.exposed = True

    def search(self, what=None, how=None, view=None,
               sensitive=None, value=None):

        self.check_index()

        out = ''

        if not what in ['info', 'source', 'repository'] \
                or not how in ['regexp', 'begins', 'exac', 'contains'] \
                or not view in ['html', 'list'] \
                or not sensitive in [None, 'on'] \
                or not isinstance(value, basestring):
            raise cherrypy.HTTPError(400, "Wrong parameter")
        else:

            lst = []

            re_flags = re.UNICODE
            vw = ''
            if sensitive == 'on':
                vw = value
            else:
                vw = value.lower()
                re_flags = re.UNICODE | re.IGNORECASE


            if what in ['source', 'repository']:

                for i in self.indexes[what]:
                    base = os.path.basename(i)

                    bw = ''
                    if sensitive == 'on':
                        bw = base
                    else:
                        bw = base.lower()

                    if what == 'repository' and not base.endswith('.asp'):
                        continue
                    elif what == 'source' \
                            and not \
                            (
                        bw.endswith('.tar') \
                            or bw.endswith('.tar.gz') \
                            or bw.endswith('.tar.bz2') \
                            or bw.endswith('.tar.lzma') \
                            or bw.endswith('.tar.xz') \
                            or bw.endswith('.zip') \
                            or bw.endswith('.7z')
                        ):
                        continue

                    if how == 'regexp' and re.match(value, base, re_flags) != None:
                        # print "-iii- RE : `%(n1)s' `%(n2)s'" % {
                        #     'n1': value,
                        #     'n2': base
                        #     }
                        lst.append(i)
                    elif how == 'begins' and bw.startswith(vw):
                        lst.append(i)
                    elif how == 'exac' and bw == vw:
                        lst.append(i)
                    elif how == 'contains' and bw.find(vw) != -1:
                        lst.append(i)

            elif what in ['info']:

                infos = self.pdb.list_pkg_info_records('*', mute=True)

                for i in infos:

                    iw = ''
                    if sensitive == 'on':
                        iw = i
                    else:
                        iw = i.lower()

                    if how == 'regexp' and re.match(value, i, re_flags) != None:
                        lst.append(i)
                    elif how == 'begins' and iw.startswith(vw):
                        lst.append(i)
                    elif how == 'exac' and iw == vw:
                        lst.append(i)
                    elif how == 'contains' and iw.find(vw) != -1:
                        lst.append(i)

            if view == 'html':
                search_html = self.templates['search'].render(
                    what = what,
                    results = lst
                    )

                out = self.templates['html'].render(
                    title = 'UHT Server',
                    body = search_html
                    )
            elif view == 'list':
                cherrypy.response.headers['Content-Type'] = 'text/plain'
                out = '%(list)s\n' % {'list': '\n'.join(lst)}


        return out

    search.exposed = True

    def infolist(self):

        self.check_index()

        lst = self.pdb.list_pkg_info_records('*', mute=True)

        toc_sl = []
        cc = ''
        for i in lst:
            if cc != i[0]:
                toc_sl.append(i[0])
                cc = i[0]

        toc_sl.sort()
        lst.sort()

        info_list = self.templates['infolist'].render(
            infos = lst,
            toc_sl = toc_sl
            )

        html = self.templates['html'].render(
            title = 'UHT Server - Info List',
            body = info_list
            )

        return html

    infolist.exposed = True


    def info(self, name):

        self.check_index()

        out = ''

        r = self.pdb.package_info_record_to_dict(name = name)
        if r == None:
            out = "Not found named info record"
        else:

            pid = self.pdb.get_package_id(name)
            if pid != None:
                category = self.pdb.get_package_path_string(pid)
            else:
                category = "< Package not indexed! >"

            regexp = '< Wrong regexp type name >'
            if r['pkg_name_type'] in name.NAME_REGEXPS:
                regexp = name.NAME_REGEXPS[r['pkg_name_type']]


            out = self.templates['info'].render(
                name = name,
                homepage = r['homepage'],
                pkg_name_type = r['pkg_name_type'],
                regexp = regexp,
                buildinfo = r['buildinfo'],
                description = r['description'],
                sources = r['sources'],
                mirrors = r['mirrors'],
                tags = r['tags'],
                category = category
                )

        html = self.templates['html'].render(
            title = name,
            body = out
            )

        return html

    info.exposed = True



    def default(self):

        raise cherrypy.HTTPRedirect('index')

    default.exposed = True



def start_host(config=None):

    ret = 0

    tpldir = os.path.dirname(os.path.abspath(__file__))

    serv_config = {
        'global': {
            'server.bind_addr' : (config['server_ip'],
                                  int(config['server_port'])),
            # 'server.socket_port' : port,
            'global.server.thread_pool' : 10,
            'error_page.default': edefault
            },
        '/files_info' :{
            'tools.staticdir.on' : True,
            'tools.staticdir.dir' : config['info']
            },
        '/files_repository' :{
            'tools.staticdir.on' : True,
            'tools.staticdir.dir' : config['repository']
            },
        '/files_source' :{
            'tools.staticdir.on' : True,
            'tools.staticdir.dir' : config['source']
            }
        # ,
        # '/css': {
        #     'tools.staticdir.on' : True,
        #     'tools.staticdir.dir' : PPWD + '/css'
        #     },
        # '/js': {
        #     'tools.staticdir.on' : True,
        #     'tools.staticdir.dir' : PPWD + '/js'
        #     }
        }

    templates = {}

    templates_error = False
    for i in ['html', 'index', 'infolist', 'info',
              'search', 'control']:
        try:
            templates[i] = Template(
                filename = os.path.join(
                    tpldir,
                    'templates',
                    '%(name)s.html' % {'name': i}
                    )
                )
        except:
            e = sys.exc_info()
            aipsetup.utils.print_exception_info(e)
            print "-e- Error reading template %(name)s" % {
                'name': os.path.join(
                    config['uhtroot'],
                    'templates',
                    '%(name)s.html' % {'name': i}
                    )
            }

            templates_error = True

    if not templates_error:
        cherrypy.quickstart(
            Index(config, templates),
            config['server_prefix'],
            serv_config)

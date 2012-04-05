#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import os.path
import traceback

import sys

import cherrypy

import aipsetup.getopt2
import aipsetup.utils
import aipsetup.pkgindex


from mako.template import Template
from mako import exceptions

def e404(status, message, traceback, version):

    return '404: page not found ^_^'

def e500(status, message, traceback, version):

    return '500: internal server error x_x'

def print_help():
    print """\
aipsetup server command

   index_uht

      create all required indexes for UHT project

   index_directory DIR

      creates DIR/index.txt with recursive list of all files in DIR

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

            for i in ['source', 'repository']:
                index_directory(
                    config[i], config['%(n)s_index' % {'n': i}])

        elif args[0] == 'index_directory':

            if len(args) == 1:

                print "-e- directory name required"
                ret = 2

            else:

                if not os.path.isdir(args[1]):
                    print "-e- not a directory"
                else:

                    index_directory(args[1],
                                    os.path.join(args[1],
                                                 'index.txt'
                                                 )
                                    )

        elif args[0] == 'start':

            start_host(config)

        else:
            print "-e- wrong command"
            ret = 1

    return ret

def _index_directory(f, root_dir, root_dirl):

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
            _index_directory(f, full_path, root_dirl)

        elif not each[0] == '.' and os.path.isfile(full_path):
            p = full_path[root_dirl:]
            f.write('%(name)s\n' % {
                    'name': p
                    })


def print_exception_info(e):

    print "-e- EXCEPTION: %(type)s" % {'type': repr(e[0])}
    print "        VALUE: %(val)s"  % {'val' : repr(e[1])}
    print "    TRACEBACK:"
    traceback.print_tb(e[2])

def index_directory(dir_name, outputfilename='index.txt'):

    dir_name = os.path.abspath(dir_name)
    dir_namel = len(dir_name)

    print "-i- indexing %(dir)s..." % {'dir': dir_name}

    f=open(outputfilename, 'w')

    _index_directory(f, dir_name, dir_namel)

    f.close()

    return 0


class Index:

    def __init__(self, config, templates):

        self.config = config
        self.templates = templates
        self.pdb = aipsetup.pkgindex.PackageDatabase(self.config)


    def reload_indexes(self):
        pass


    def index_html(self, mode=None):

        index = self.templates['index'].render(
            )

        html = self.templates['html'].render(
            title = 'UHT Server',
            body = index
            )

        return html

    index_html.exposed = True

    def search(self):
        return ''

    search.exposed = True

    def infolist_html(self):

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
            title = 'UHT Server',
            body = info_list
            )

        return html

    infolist_html.exposed = True


    def info(self, name):

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

            out = self.templates['info'].render(
                name = name,
                homepage = r['homepage'],
                pkg_name_type = r['pkg_name_type'],
                regexp = r['regexp'],
                builder = r['builder'],
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

        raise cherrypy.HTTPRedirect('index.html')

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

            # 'hooks.before_request_body' : brb_hook,

            'error_page.404': e404,
            'error_page.500': e500
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
    for i in ['html', 'index', 'infolist', 'info']:
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
            print_exception_info(e)
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

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import os.path

import sys

import cherrypy

import aipsetup.getopt2
import aipsetup.utils

from mako.template import Template
from mako import exceptions


def e404(status, message, traceback, version):

    return '404: page not found ^_^'

def e500(status, message, traceback, version):

    return '500: internal server error x_x'

class Index:

    def __init__(self, root_dir):

        self.root_dir = root_dir

        self.templates = {}

        for i in ['html', 'index']:
            templates[i] = Template(
                filename = os.path.join(
                    self.root_dir,
                    'server_files',
                    'templates',
                    '%(name)s.html' % {'name': i}
                    )
                )

    def reload_indexes(self):
        pass


    def index_html(self, mode=None):

        html_t = Template(filename = os.path.join(PPWD, 'templates', 'index.html'))

        html = templates['html'].render()

        return html

    index_html.exposed = True


    def default(self):

        raise cherryppy.HTTPRedirect('index.html')

    default.exposed = True



def start_host(root_dir, ip='127.0.0.1', port=8005, http_prefix='/', config=None):

    ret = 0

    if config == None:

        config = aipsetup.utils.load_config()
        if config == None:
            ret = 1


    serv_config = {
        'global': {'server.socket_port' : port,
                   'global.server.thread_pool' : 10,

                   #               'hooks.before_request_body' : brb_hook,

                   'error_page.404': e404,
                   'error_page.500': e500
                   },
        http_prefix+'info_files' :{
            'tools.staticdir.on' : True,
            'tools.staticdir.dir' : '/css'
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

    cherrypy.quickstart(Index(indexfilename = os.path.join()), '/', serv_config)

if __name__ == '__main__':

    ret = 0

    opt, args = aipsetup.getopt2(sys.argv[1:])

    ip = '127.0.0.1'
    port = 8005
    root_dir = ''
    http_prefix='/'

    if len(args) == 0 or not os.path.isdir(args[0]):
        print "-e- Hosting root not specified"
        ret = 1
    else:

        root_dir = args[0]

        for i in opt:
            if (i[0] == '--address' or i[0] == '-a') and  i[1] != None:
                ip = i[1]

        for i in opt:
            if (i[0] == '--port' or i[0] == '-p') and  i[1] != None:
                port = i[1]


        start_host(root_dir, ip, port, http_prefix)

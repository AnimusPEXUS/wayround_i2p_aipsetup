
"""
UNICORN distro serving related stuff
"""

import os.path
import xml.sax.saxutils
import json
import copy
import functools

import cherrypy
import cherrypy.lib


import org.wayround.aipsetup.pkgindex
import org.wayround.aipsetup.config
import org.wayround.aipsetup.serverui


TEXT_PLAIN = 'text/plain; codepage=utf-8'
APPLICATION_JSON = 'application/json; codepage=utf-8'


def edefault(status, message, traceback, version):

    return "%(status)s: %(message)s" % {
        'message': xml.sax.saxutils.escape(message),
        'status': str(status)
        }

def exported_commands():
    return {
        'start': server_start_host
        }

def commands_order():
    return ['start']



def server_start_host(opts, args):
    """
    Start serving UNICORN Web Host
    """
    return start_host()



class Index:

    def index(self):

        txt = org.wayround.aipsetup.serverui.page_index()

        return txt

    index.exposed = True


    def category(self, path=None, mode=None):

        if mode == None:
            mode = 'html'

        if not mode in ['html', 'json']:
            raise cherrypy.HTTPError(400, "Wrong `mode' parameter")

        txt = ''
        if mode == 'html':

            if path == None:
                path = ''

            db = org.wayround.aipsetup.pkgindex.PackageDatabase()

            txt = org.wayround.aipsetup.serverui.page_category(db, path)

            db.close()

        elif mode == 'json':

            db = org.wayround.aipsetup.pkgindex.PackageDatabase()

            if path == None:

                pkgs = db.ls_package_dict(None)

                cats = db.ls_category_dict(None)

            else:
                cid = db.get_category_by_path(path)

                pkgs = db.ls_package_dict(cid)

                cats = db.ls_category_dict(cid)

            for i in list(pkgs.keys()):
                pkgs[i] = db.get_package_path_string(i)

            for i in list(cats.keys()):
                cats[i] = db.get_category_path_string(i)

            db.close()



            txt = json.dumps(
                {
                    'packages': pkgs,
                    'categories': cats
                    },
                indent=2,
                sort_keys=True
                )

            txt = bytes(txt, 'utf-8')

            cherrypy.response.headers['Content-Type'] = APPLICATION_JSON

        return txt

    category.exposed = True

    def package(self, name='', mode='normal'):

        if name == '' or name.isspace():
            raise cherrypy.HTTPError(400, "Wrong `name' parameter")

        if not mode in ['normal', 'sources', 'packages', 'info']:
            raise cherrypy.HTTPError(400, "Wrong `mode' parameter")

        txt = ''
        if mode == 'normal':

            db = org.wayround.aipsetup.pkgindex.PackageDatabase()

            txt = org.wayround.aipsetup.serverui.page_package(db, name)

            del db
        elif mode == 'packages':

            files = org.wayround.aipsetup.pkgindex.get_package_files(name)

            files.sort(
                reverse=True,
                key=functools.cmp_to_key(
                    org.wayround.aipsetup.version.package_version_comparator
                    )
                )

            l = len(files)
            i = -1
            while i != l - 1:
                i += 1
                files[i] = 'files_repository' + files[i]

            txt = json.dumps(files, indent=2, sort_keys=True)

            cherrypy.response.headers['Content-Type'] = APPLICATION_JSON


        elif mode == 'sources':
            files = org.wayround.aipsetup.pkgindex.get_package_source_files(name)
            files.sort(reverse=True)

            l = len(files)
            i = -1
            while i != l - 1:
                i += 1
                files[i] = 'files_source' + files[i]

            txt = json.dumps(files, indent=2, sort_keys=True)

            cherrypy.response.headers['Content-Type'] = APPLICATION_JSON


        elif mode == 'info':

            db = org.wayround.aipsetup.pkgindex.PackageDatabase()
            r = db.package_info_record_to_dict(name=name)

            cid = db.get_package_category_by_name(name)
            if cid != None:
                category = db.get_category_path_string(cid)
            else:
                category = "< Package not indexed! >"


            info = copy.copy(r)
            info['tags'] = ', '.join(r['tags'])
            info['category'] = category
            info['newest_pkg'] = (
                org.wayround.aipsetup.pkgindex.latest_package(name, db)
                )
            info['newest_src'] = (
                org.wayround.aipsetup.pkgindex.latest_source(name, db)
                )

            del db

            txt = json.dumps(info, indent=2, sort_keys=True)

            cherrypy.response.headers['Content-Type'] = APPLICATION_JSON

        else:
            txt = ''

        if cherrypy.response.headers['Content-Type'] in [TEXT_PLAIN, APPLICATION_JSON]:
            if isinstance(txt, str):
                txt = txt.encode(encoding='utf-8', errors='strict')

        return txt

    package.exposed = True



def start_host():

    ret = 0

    tpldir = os.path.dirname(os.path.abspath(__file__))

    serv_config = {
        'global': {
            'server.bind_addr' : (org.wayround.aipsetup.config.config['server_ip'],
                                  int(org.wayround.aipsetup.config.config['server_port'])),
            # 'server.socket_port' : port,
            'global.server.thread_pool' : 10,
            'error_page.default': edefault
            },
        '/files_info' :{
            'tools.staticdir.on' : True,
            'tools.staticdir.dir' : org.wayround.aipsetup.config.config['info']
            },
        '/files_repository' :{
            'tools.staticdir.on' : True,
            'tools.staticdir.dir' : org.wayround.aipsetup.config.config['repository'],
            'tools.staticdir.content_types' : {
                'asp': 'binary',
                }
            },
        '/files_source' :{
            'tools.staticdir.on' : True,
            'tools.staticdir.dir' : org.wayround.aipsetup.config.config['source'],
            'tools.staticdir.content_types' : {
                'gz': 'binary',
                'bz2': 'binary',
                'xz': 'binary',
                '7z': 'binary',
                'lzma': 'binary'
                }
            },
         '/css': {
             'tools.staticdir.on' : True,
             'tools.staticdir.dir' :
                os.path.abspath(
                    org.wayround.aipsetup.config.config['server_files']
                    ),
            'tools.staticdir.content_types' : {
                'css': 'text/css; codepage=utf-8',
                }
             },
        # '/js': {
        #     'tools.staticdir.on' : True,
        #     'tools.staticdir.dir' : PPWD + '/js'
        #     }
        }


    cherrypy.quickstart(
        Index(),
        org.wayround.aipsetup.config.config['server_path'],
        serv_config
        )

    return ret

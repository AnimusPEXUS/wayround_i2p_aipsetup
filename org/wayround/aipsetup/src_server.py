
"""
Light source tarball http server
"""

import os.path
import fnmatch
import re
import urllib.request
import functools

import bottle

from mako.template import Template

import org.wayround.aipsetup.config
import org.wayround.aipsetup.dbconnections
import org.wayround.utils.version

def cli_name():
    """
    Internally used by aipsetup
    """
    return 'src_server'


def exported_commands():
    """
    Internally used by aipsetup
    """
    return {
        'start': src_server_start
        }

def commands_order():
    """
    Internally used by aipsetup
    """
    return [
        'start'
        ]

def src_server_start(opts, args):

    """
    Starts serving specifed host and port

    aipsetup3 src_server start [--host=localhost] [--port=8080]

    Requires aipsetup configuration file to be correctly configured with
    'source' and 'source_index' parameters
    """

    ret = 0

    host = 'localhost'
    port = 8080

    if '--host' in opts:
        host = opts['--host']

    if '--port' in opts:
        port = int(opts['--port'])

    serv = SRCServer(
        org.wayround.aipsetup.config.config['source'],
        org.wayround.aipsetup.dbconnections.src_db(),
        host=host,
        port=port
        )

    serv.start()

    return ret

class SRCServer:

    def __init__(self, server_dir, src_db, host='localhost', port=8080):

        self.server_dir = os.path.abspath(server_dir)

        self.src_db = src_db

        self.host = host
        self.port = port

        self.template_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'templates',
            'src_server'
            )

        self.app = bottle.Bottle()

        self.app.route('', method='GET', callback=self.none)

        self.app.route('/', method='GET', callback=self.index)
        self.app.route('/list', method='GET', callback=self.get_tag_list)
        self.app.route('/files', method='GET', callback=self.get_file_list)
        self.app.route('/download/<path:path>', method='GET', callback=self.download)

        self.templates = {}

        for i in [
            'html', 'tag_list', 'file_list', 'search'
            ]:
            self.templates[i] = Template(
                filename=os.path.join(self.template_dir, '{}.html'.format(i)),
                format_exceptions=False
                )

    def start(self):
        bottle.run(self.app, host=self.host, port=self.port)

    def search(self, mode='filemask', mask='*', cs=True):
        return self.templates['search'].render(mode=mode, mask=mask, cs=cs)

    def none(self):
        bottle.response.set_header('Location', '/')
        bottle.response.status = 303
        return ''

    def index(self):
        ret = self.templates['html'].render(
            title="Index",
            body=self.search(),
            css=[]
            )
        return ret

    def get_tag_list(self):

        decoded_params = bottle.request.params.decode('utf-8')

        if not 'action' in decoded_params:
            decoded_params['action'] = 'search'

        if not decoded_params['action'] in ['search', 'go']:
            raise bottle.HTTPError(400, 'Wrong action parameter')

        if not 'mode' in decoded_params:
            decoded_params['mode'] = 'filemask'

        if not 'mask' in decoded_params:
            decoded_params['mask'] = '*'

        if not 'cs' in decoded_params:
            decoded_params['cs'] = 'off'


        if not decoded_params['cs'] == 'on':
            decoded_params['cs'] = 'off'

        if not decoded_params['mode'] in ['filemask', 'regexp']:
            raise bottle.HTTPError(400, 'Wrong mode parameter')

        mode = decoded_params['mode']
        mask = decoded_params['mask']
        cs = decoded_params['cs'] == 'on'
        action = decoded_params['action']

        ret = ''

        if action == 'go':
            bottle.response.set_header(
                'Location',
                '/files?name={}'.format(urllib.request.quote(mask))
                )
            bottle.response.status = 303
            ret = ''

        else:

            if not cs:
                mask = mask.lower()

            mode_name = ''
            if mode == 'filemask':
                mode_name = 'File Name Mask'
            elif mode == 'regexp':
                mode_name = 'Regular Expression'

            cs_name = ''
            if cs:
                cs_name = 'Case Sensitive'
            else:
                cs_name = 'None Case Sensitive'

            all_tags = self.src_db.get_all_tags()
            filtered_tags = []

            for i in all_tags:

                if not cs:
                    i = i.lower()

                if (
                    (mode == 'filemask' and fnmatch.fnmatch(i, mask)) or
                    (mode == 'regexp' and re.match(mask, i))
                    ):
                    filtered_tags.append(i)

            filtered_tags.sort()

            ret = self.templates['html'].render(
                title="List of package names found by request mode "
                    "`{}', using mask `{}' in `{}' mode".format(
                    mode_name,
                    mask,
                    cs_name
                    ),
                body=self.search(mode=mode, mask=mask, cs=cs)
                    + self.templates['tag_list'].render(tags=filtered_tags),
                css=[]
                )

        return ret

    def get_file_list(self):

        for i in [
            'name'
            ]:
            if not i in bottle.request.params:
                raise bottle.HTTPError(400, "parameter `{}' must be passed".format(i))

        decoded_params = bottle.request.params.decode('utf-8')

        results = self.src_db.get_objects_by_tag(decoded_params['name'])

        results.sort(
            reverse=True,
            key=functools.cmp_to_key(
                org.wayround.utils.version.source_version_comparator
                )
            )

        ret = self.templates['html'].render(
            title="List of tarballs with basename `{}'".format(
                decoded_params['name']
                ),
            body=self.search(mode='filemask', mask=decoded_params['name'], cs=True)
                + self.templates['file_list'].render(files=results),
            css=[]
            )

        return ret

    def download(self, path):

        return bottle.static_file(path, root=self.server_dir, mimetype='binary')

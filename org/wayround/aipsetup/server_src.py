
"""
Light source tarball http server
"""

import fnmatch
import functools
import json
import os.path
import re
import urllib.request

import bottle
from mako.template import Template

import org.wayround.aipsetup.config
import org.wayround.aipsetup.dbconnections
import org.wayround.aipsetup.repository
import org.wayround.utils.version


APPLICATION_JSON = 'application/json; codepage=utf-8'


def src_server_start(command_name, opts, args, adds):

    """
    Starts serving specified host and port

    aipsetup3 src_server start [--host=localhost] [--port=8080]

    Requires aipsetup configuration file to be correctly configured with
    'source' and 'source_index' parameters
    """

    config = adds['config']

    ret = 0

    host = config['src_tarball_server']['host']
    port = config['src_tarball_server']['port']

    os.chdir(config['src_tarball_server']['working_dir'])

    serv = SRCServer(
        config['src_tarball_server']['tarball_repository_root'],
        org.wayround.aipsetup.dbconnections.src_repo_db_new_connection(
            config['src_tarball_server']['src_index_db_config']
            ),
        host=host,
        port=port
        )

    serv.start()

    return ret


def src_server_reindex(command_name, opts, args, adds):

    """
    Tarball sources server index tool

    options:
        --force                 force total reindex
        --first-delete-found    delete found tarballs from index before doing
                                anything else
        --clean-only            only remove non existing tarballs from index
    """

    config = adds['config']

    con = org.wayround.aipsetup.dbconnections.src_repo_db_new_connection(
        config['src_tarball_server']['src_index_db_config']
        )

    ctl = org.wayround.aipsetup.repository.SourceRepoCtl(
        config['src_tarball_server']['tarball_repository_root'],
        con
        )

    ctl.index_sources(
        config['src_tarball_server']['tarball_repository_root'],
        config['src_tarball_server']['acceptable_src_file_extensions'],
        '--force' in opts,
        '--first-delete-found' in opts,
        '--clean-only'  in opts
        )

    return 0


class SRCServer:

    def __init__(self, server_dir, src_db, host='localhost', port=8080):

        self.server_dir = os.path.abspath(server_dir)

        self.src_db = src_db

        self.host = host
        self.port = port

        self.template_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'web',
            'src_server',
            'templates',
            )

        self.app = bottle.Bottle()

        self.app.route('', method='GET', callback=self.none)

        self.app.route('/', method='GET', callback=self.index)
        self.app.route('/list', method='GET', callback=self.get_tag_list)
        self.app.route('/files', method='GET', callback=self.get_file_list)
        self.app.route(
            '/download/<path:path>', method='GET', callback=self.download
            )

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

    def search(self, searchmode='filemask', mask='*', cs=True):
        return self.templates['search'].render(searchmode=searchmode, mask=mask, cs=cs)

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

        if not 'searchmode' in decoded_params:
            decoded_params['searchmode'] = 'filemask'

        if not 'mask' in decoded_params:
            decoded_params['mask'] = '*'

        if not 'resultmode' in decoded_params:
            decoded_params['resultmode'] = 'html'

        if not 'cs' in decoded_params:
            decoded_params['cs'] = 'off'

        if not decoded_params['cs'] == 'on':
            decoded_params['cs'] = 'off'

        if not decoded_params['resultmode'] in ['html', 'json']:
            raise bottle.HTTPError(400, 'Wrong resultmode parameter')

        if not decoded_params['searchmode'] in ['filemask', 'regexp']:
            raise bottle.HTTPError(400, 'Wrong searchmode parameter')

        resultmode = decoded_params['resultmode']
        searchmode = decoded_params['searchmode']
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

            searchmode_name = ''
            if searchmode == 'filemask':
                searchmode_name = 'File Name Mask'
            elif searchmode == 'regexp':
                searchmode_name = 'Regular Expression'

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
                    (searchmode == 'filemask' and fnmatch.fnmatch(i, mask)) or
                    (searchmode == 'regexp' and re.match(mask, i))
                    ):
                    filtered_tags.append(i)

            filtered_tags.sort()

            ret = ''

            if resultmode == 'html':
                ret = self.templates['html'].render(
                    title="List of package names found by request mode "
                        "`{}', using mask `{}' in `{}' mode".format(
                        searchmode_name,
                        mask,
                        cs_name
                        ),
                    body=self.search(searchmode=searchmode, mask=mask, cs=cs)
                        +
                        self.templates['tag_list'].render(tags=filtered_tags),
                    css=[]
                    )

            elif resultmode == 'json':
                ret = json.dumps(filtered_tags, sort_keys=True, indent=2)
                bottle.response.set_header('Content-Type', APPLICATION_JSON)

        return ret

    def get_file_list(self):

        for i in [
            'name'
            ]:
            if not i in bottle.request.params:
                raise bottle.HTTPError(
                    400,
                    "parameter `{}' must be passed".format(i)
                    )

        decoded_params = bottle.request.params.decode('utf-8')

        if not 'resultmode' in decoded_params:
            decoded_params['resultmode'] = 'html'

        if not decoded_params['resultmode'] in ['html', 'json']:
            raise bottle.HTTPError(400, 'Wrong resultmode parameter')

        resultmode = decoded_params['resultmode']

        results = self.src_db.get_objects_by_tag(decoded_params['name'])

        results.sort(
            reverse=True,
            key=functools.cmp_to_key(
                org.wayround.utils.version.source_version_comparator
                )
            )

        ret = ''

        if resultmode == 'html':

            ret = self.templates['html'].render(
                title="List of tarballs with basename `{}'".format(
                    decoded_params['name']
                    ),
                body=self.search(
                    searchmode='filemask',
                    mask=decoded_params['name'],
                    cs=True
                    )
                    + self.templates['file_list'].render(files=results),
                css=[]
                )

        elif resultmode == 'json':
            ret = json.dumps(results, sort_keys=True, indent=2)
            bottle.response.set_header('Content-Type', APPLICATION_JSON)

        return ret

    def download(self, path):

        return bottle.static_file(
            path, root=self.server_dir, mimetype='binary'
            )
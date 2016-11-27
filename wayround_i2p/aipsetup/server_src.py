
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

import wayround_org.aipsetup.controllers
import wayround_org.aipsetup.dbconnections
import wayround_org.utils.version


APPLICATION_JSON = 'application/json; codepage=utf-8'


def src_server_start(command_name, opts, args, adds):
    """
    Starts serving specified host and port

    aipsetup3 src_server start

    Requires aipsetup configuration file to be correctly configured with
    'source' and 'source_index' parameters
    """

    config = adds['config']

    ret = 0

    host = config['src_server']['host']
    port = config['src_server']['port']

    os.chdir(config['src_server']['working_dir'])

    serv = SRCServer(
        config['src_server']['tarball_repository_root'],
        wayround_org.aipsetup.dbconnections.src_repo_db(
            config
            ),
        host=host,
        port=int(port),
        acceptable_source_name_extensions=(
            config['src_server']['acceptable_src_file_extensions'].split()
            )
        )

    serv.start()

    return ret


def src_server_reindex(command_name, opts, args, adds):

    """
    Tarball sources server index tool

    options:
        --force                 force total reindex
        --first-delete-found    delete found tarballs from index before doing
                                anything else to force they'r reparsing
        --clean-only            only remove non existing tarballs from index
    """

    config = adds['config']

    ctl = wayround_org.aipsetup.controllers.src_repo_ctl_by_config(config)

    ctl.index_sources(
        config['src_server']['tarball_repository_root'],
        config['src_server']['acceptable_src_file_extensions'].split(),
        '--force' in opts,
        '--first-delete-found' in opts,
        '--clean-only' in opts
        )

    return 0


class SRCServer:

    def __init__(
        self,
        repository_dir,
        src_db,
        host='localhost', port=8080,
        acceptable_source_name_extensions=None
        ):

        self.repository_dir = os.path.abspath(repository_dir)

        self.src_db = src_db
        self.acceptable_source_name_extensions = \
            acceptable_source_name_extensions

        self.host = host
        self.port = port

        self.template_dir = wayround_org.utils.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'web',
            'src_server',
            'templates',
            )

        self.app = bottle.Bottle()

        self.app.route('', method='GET', callback=self.none)

        self.app.route('/', method='GET', callback=self.index)
        self.app.route('/search', method='GET', callback=self.search)
        self.app.route('/files', method='GET', callback=self.get_file_list)
        self.app.route(
            '/download/<path:path>', method='GET', callback=self.download
            )

        self.templates = {}

        for i in [
            'html', 'tag_list', 'file_list', 'search'
            ]:
            self.templates[i] = Template(
                filename=wayround_org.utils.path.join(self.template_dir, '{}.html'.format(i)),
                format_exceptions=False
                )

    def start(self):
        bottle.run(self.app, host=self.host, port=self.port)

    def search_tpl(
        self,
        searchmode='filemask', mask='*', cs=True
        ):
        return self.templates['search'].render(
            searchmode=searchmode,
            mask=mask,
            cs=cs
            )

    def none(self):
        bottle.response.set_header('Location', '/')
        bottle.response.status = 303
        return ''

    def index(self):
        ret = self.templates['html'].render(
            title="Index",
            body=self.search_tpl(),
            css=[]
            )
        return ret

    def search(self):

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

                look_for = i

                if not cs:
                    look_for = look_for.lower()

                if (
                    (searchmode == 'filemask' and fnmatch.fnmatch(look_for, mask)) or
                    (searchmode == 'regexp' and re.match(mask, look_for))
                    ):
                    filtered_tags.append(i)

            filtered_tags.sort()

            ret = ''

            if resultmode == 'html':
                ret = self.templates['html'].render(
                    title="List of tarball names found by request mode "
                        "`{}', using mask `{}' in `{}' mode".format(
                        searchmode_name,
                        mask,
                        cs_name
                        ),
                    body=self.search_tpl(
                        searchmode=searchmode,
                        mask=mask,
                        cs=cs
                        )
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

        name = decoded_params['name']

        pkgname = name

        pkgname_paths = None

        if pkgname == None:
            pkgname = ''

        if 'paths' in decoded_params:
            pkgname_paths = json.loads(decoded_params['paths'])

        if type(pkgname_paths) != list:
            pkgname_paths = []

        if len(pkgname_paths) == 0:
            pkgname_paths.append('')

        if name == '' or name.isspace():
            raise bottle.HTTPError(400, "`name' must be non empty")

        if not 'resultmode' in decoded_params:
            decoded_params['resultmode'] = 'html'

        if not decoded_params['resultmode'] in ['html', 'json']:
            raise bottle.HTTPError(400, 'Wrong resultmode parameter')

        resultmode = decoded_params['resultmode']

        results = self.src_db.get_objects_by_tag(name)

        if pkgname != '':
            for i in range(len(results) - 1, -1, -1):

                found = False
                for j in pkgname_paths:
                    if results[i].startswith(j):
                        found = True
                        break

                if not found:
                    del results[i]

        def source_version_comparator(v1, v2):
            return wayround_org.utils.version.source_version_comparator(
                v1, v2,
                self.acceptable_source_name_extensions
                )

        results.sort(
            reverse=True,
            key=functools.cmp_to_key(
                source_version_comparator
                )
            )

        ret = ''

        if resultmode == 'html':

            ret = self.templates['html'].render(
                title="List of tarballs with basename `{}'".format(name),
                body=self.search_tpl(
                    searchmode='filemask',
                    mask=name,
                    cs=True
                    )
                    + self.templates['file_list'].render(
                        files=results,
                        name=name
                        ),
                css=[]
                )

        elif resultmode == 'json':
            ret = json.dumps(results, sort_keys=True, indent=2)
            bottle.response.set_header('Content-Type', APPLICATION_JSON)

        return ret

    def download(self, path):

        return bottle.static_file(
            path, root=self.repository_dir, mimetype='binary'
            )

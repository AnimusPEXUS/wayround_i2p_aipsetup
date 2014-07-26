
import collections
import fnmatch
import functools
import json
import logging
import os.path
import re

import bottle

import org.wayround.aipsetup.controllers
import org.wayround.aipsetup.server_pkg_ui
import org.wayround.aipsetup.client_src
import org.wayround.utils.version
import org.wayround.utils.tarball


TEXT_PLAIN = 'text/plain; codepage=utf-8'
APPLICATION_JSON = 'application/json; codepage=utf-8'


def server_start_host(command_name, opts, args, adds):
    """
    Start serving UNICORN ASP packages Web Server
    """

    config = adds['config']

    pkg_repo_ctl = \
        org.wayround.aipsetup.controllers.pkg_repo_ctl_by_config(config)

    info_ctl = \
        org.wayround.aipsetup.controllers.info_ctl_by_config(config)

    tag_ctl = \
        org.wayround.aipsetup.controllers.tag_ctl_by_config(config)

    bundles_ctl = \
        org.wayround.aipsetup.controllers.bundles_ctl_by_config(config)

    app = ASPServer(
        pkg_repo_ctl,
        info_ctl,
        tag_ctl,
        bundles_ctl,
        config['pkg_server']['host'],
        int(config['pkg_server']['port']),
        config['src_client']['server_url'],
        acceptable_source_name_extensions=(
            config['src_client']['acceptable_src_file_extensions']
            )
        )

    app.start()

    return 0


class ASPServer:

    def __init__(
            self,
            pkg_repo_ctl,
            info_ctl,
            tag_ctl,
            bundles_ctl,
            host='localhost',
            port=8081,
            src_page_url='https://localhost:8080/',
            acceptable_source_name_extensions=None
            ):

        self._src_page_url = src_page_url

        web = os.path.join(os.path.dirname(__file__), 'web', 'pkg_server')

        templates_dir = os.path.join(web, 'templates')
        css_dir = os.path.join(web, 'css')
        js_dir = os.path.join(web, 'js')

        # TODO: extinct self.config
        #        self.config = config

        self.host = host
        self.port = port

        self.templates_dir = templates_dir
        self.css_dir = css_dir
        self.js_dir = js_dir

        self.pkg_repo_ctl = pkg_repo_ctl
        self.info_ctl = info_ctl
        self.tag_ctl = tag_ctl
        self.bundles_ctl = bundles_ctl

        self.acceptable_source_name_extensions = \
            acceptable_source_name_extensions

        self.ui = org.wayround.aipsetup.server_pkg_ui.UI(templates_dir)

        self.app = bottle.Bottle()

        self.app.route('/', 'GET', self.index)

        self.app.route('/js/<filename>', 'GET', self.js)
        self.app.route('/css/<filename>', 'GET', self.css)

        self.app.route('/category', 'GET', self.category_redirect)
        self.app.route('/category/', 'GET', self.category)
        self.app.route('/category/<path:path>', 'GET', self.category)
        self.app.route('/package', 'GET', self.package_redir)
        self.app.route('/package/<name>', 'GET', self.package)
        self.app.route('/package/<name>/asps', 'GET', self.asps)
#        self.app.route('/package/<name>/asps_latest', 'GET', self.asps_latest)
        self.app.route('/package/<name>/tarballs', 'GET', self.tarballs)
#        self.app.route(
#            '/package/<name>/tarballs_latest', 'GET', self.tarballs_latest
#            )

        self.app.route('/search', 'GET', self.search)

        self.app.route(
            '/package/<name>/asps/<name2>', 'GET', self.download_pkg
            )

        self.app.route('/name_by_name', 'GET', self.name_by_name)

        self.app.route('/bundles', 'GET', self.bundles)
        self.app.route('/bundles/<name>', 'GET', self.download_bundle)

        return

    def start(self):
        return bottle.run(self.app, host=self.host, port=self.port)

    def index(self):

        ret = self.ui.html(
            title="Index",
            body=self.ui.index(
                self.ui.search()
                )
            )

        return ret

    def css(self, filename):
        return bottle.static_file(filename, root=self.css_dir)

    def js(self, filename):
        return bottle.static_file(filename, root=self.js_dir)

    def download_pkg(self, name, name2):

        base = os.path.basename(name2)

        path = self.pkg_repo_ctl.get_package_path_string(name)

        filename = org.wayround.utils.path.abspath(
            org.wayround.utils.path.join(
                self.pkg_repo_ctl.get_repository_dir(), path, 'pack', base
                )
            )

        if not filename.startswith(
                self.pkg_repo_ctl.get_repository_dir() + os.path.sep
                ):
            raise bottle.HTTPError(404, "Wrong package name `{}'".format(name))

        if not os.path.isfile(filename):
            raise bottle.HTTPError(404, "File `{}' not found".format(base))

        return bottle.static_file(
            filename=base,
            root=os.path.dirname(filename),
            mimetype='application/binary'
            )

    def category_redirect(self):
        bottle.response.set_header('Location', '/category/')
        bottle.response.status = 303

    def category(self, path=None):

        decoded_params = bottle.request.params.decode('utf-8')

        resultmode = None

        if not 'resultmode' in decoded_params:
            resultmode = 'html'
        else:
            resultmode = decoded_params['resultmode']
            if not resultmode in ['html', 'json']:
                raise bottle.HTTPError(400, "Invalid resultmode")

        ret = ''
        if resultmode == 'html':

            if path in [None, '/']:
                path = ''

            cat_id = self.pkg_repo_ctl.get_category_by_path(
                path
                )

            if cat_id == None:
                return bottle.HTTPError(404, "Category not found")

            double_dot = ''

            if cat_id != 0:

                parent_id = self.pkg_repo_ctl.get_category_parent_by_id(
                    cat_id
                    )

                parent_path = self.pkg_repo_ctl.get_category_path_string(
                    parent_id
                    )

                double_dot = self.ui.category_double_dot(parent_path)

            categories = []
            packages = []

            cats_ids = self.pkg_repo_ctl.get_category_id_list(
                cat_id
                )

            pack_ids = self.pkg_repo_ctl.get_package_id_list(
                cat_id
                )

            for i in cats_ids:
                categories.append(
                    {'path':
                        self.pkg_repo_ctl.get_category_path_string(
                            i
                            ),
                     'name': self.pkg_repo_ctl.get_category_by_id(
                            i
                            )
                     }
                )

            for i in pack_ids:
                packages.append(
                    self.pkg_repo_ctl.get_package_by_id(
                        i
                        )
                    )

            categories.sort(key=(lambda x: x['name']))
            packages.sort()

            txt = self.ui.category(path, double_dot, categories, packages)

            ret = self.ui.html(
                title="Category: '{}'".format(path),
                body=txt
                )

        elif resultmode == 'json':

            if path in [None, '/']:
                path = ''

            cat_id = self.pkg_repo_ctl.get_category_by_path(
                path
                )

            if cat_id == None:
                return bottle.HTTPError(404, "Category not found")

            cats_ids = self.pkg_repo_ctl.get_category_id_list(
                cat_id
                )

            pack_ids = self.pkg_repo_ctl.get_package_id_list(
                cat_id
                )

            cats = []
            for i in cats_ids:
                cats.append(self.pkg_repo_ctl.get_category_by_id(i))
            cats.sort()

            pkgs = []
            for i in pack_ids:
                pkgs.append(self.pkg_repo_ctl.get_package_by_id(i))
            pkgs.sort()

            ret = json.dumps(
                {
                    'packages': pkgs,
                    'categories': cats
                    },
                indent=2,
                sort_keys=True
                )

            bottle.response.set_header('Content-Type', APPLICATION_JSON)

        return ret

    def package_redir(self):
        decoded_params = bottle.request.params.decode('utf-8')

        if not 'name' in decoded_params:
            bottle.response.set_header('Location', '/')
            bottle.response.status = 303
        else:
            bottle.response.set_header(
                'Location',
                '/package/{}'.format(decoded_params['name'])
                )
            bottle.response.status = 303

        return

    def package(self, name):

        decoded_params = bottle.request.params.decode('utf-8')

        resultmode = 'html'
        if 'resultmode' in decoded_params:
            resultmode = decoded_params['resultmode']

        if not resultmode in ['html', 'json']:
            raise bottle.HTTPError(400, "Invalid resultmode")

        pkg_info = self.info_ctl.get_package_info_record(name)
        if not pkg_info:
            raise bottle.HTTPError(404, "Not found")

        if resultmode == 'html':

            keys = list(org.wayround.aipsetup.info.
                        SAMPLE_PACKAGE_INFO_STRUCTURE_TITLES.keys())

            rows = collections.OrderedDict()

            for i in [
                    'tags', 'name', 'description', 'newest_src', 'newest_pkg'
                    ]:
                if i in keys:
                    keys.remove(i)

            for i in keys:

                rows[i] = (
                    org.wayround.aipsetup.info.
                    SAMPLE_PACKAGE_INFO_STRUCTURE_TITLES[i],
                    str(pkg_info[i])
                    )

            cid = self.pkg_repo_ctl.get_package_category_by_name(name)
            if cid != None:
                category = self.pkg_repo_ctl.get_category_path_string(cid)
            else:
                category = "< Package not categorized! >"

            tag_db = self.tag_ctl.tag_db
            tags = tag_db.get_tags(name)

            txt = self.ui.package(
                name,
                autorows=rows,
                category=category,
                description=pkg_info['description'],
                tags=tags,
                src_page_url=self._src_page_url
                )

            ret = self.ui.html(
                title="Package: '{}'".format(name),
                body=txt
                )
        else:
            ret = json.dumps(pkg_info, indent=2, sort_keys=True)
            bottle.response.set_header('Content-Type', APPLICATION_JSON)

        return ret

    def asps(self, name):

        decoded_params = bottle.request.params.decode('utf-8')

        ret = ''

        resultmode = 'html'
        if 'resultmode' in decoded_params:
            resultmode = decoded_params['resultmode']

        if not resultmode in ['html', 'json']:
            raise bottle.HTTPError(400, "Invalid resultmode")

        filesl = self.pkg_repo_ctl.get_package_files(name)
        if not isinstance(filesl, list):
            raise bottle.HTTPError(
                404,
                "Error getting file list. Is package name correct?"
                )

        filesl.sort(
            key=functools.cmp_to_key(
                org.wayround.aipsetup.version.package_version_comparator
                ),
            reverse=True
            )

        if resultmode == 'html':

            files = []
            for i in filesl:

                base = os.path.basename(i)

                stat = os.stat(
                    org.wayround.utils.path.join(
                        self.pkg_repo_ctl.get_repository_dir(),
                        i
                        )
                    )

                parsed = org.wayround.aipsetup.package_name_parser.\
                    package_name_parse(
                        base
                        )

                files.append(
                    {'basename': base,
                     'size': stat.st_size,
                     'version': parsed['groups']['version'],
                     'timestamp': parsed['groups']['timestamp']
                     }
                    )

            asp_files = self.ui.asps_file_list(files, name)

            txt = self.ui.asps(
                name, asp_files
                )

            ret = self.ui.html(
                title="Package: '{}'".format(name),
                body=txt
                )

        elif resultmode == 'json':

            files = []
            for i in filesl:

                base = os.path.basename(i)

                files.append("/package/{}/asps/{}".format(name, base))

            ret = json.dumps(files, sort_keys=True, indent=2)
            bottle.response.set_header('Content-Type', APPLICATION_JSON)

        return ret

    def tarballs(self, name):

        decoded_params = bottle.request.params.decode('utf-8')

        ret = ''

        resultmode = 'html'
        if 'resultmode' in decoded_params:
            resultmode = decoded_params['resultmode']

        if not resultmode in ['html', 'json']:
            raise bottle.HTTPError(400, "Invalid resultmode")

        rec = self.info_ctl.get_package_info_record(name)

        if rec == None:
            raise bottle.HTTPError(404, "Can't get package information")

        basename = rec['basename']
        filters = rec['filters']

        filesl = org.wayround.aipsetup.client_src.files(
            self._src_page_url, basename
            )

        if not filesl:
            raise bottle.HTTPError(404, "Error getting tarball list")

        if filesl == None:
            filesl = []

        filesl = (
            org.wayround.utils.tarball.filter_tarball_list(
                filesl,
                filters
                )
            )

        if not isinstance(filesl, list):
            raise bottle.HTTPError(500, "tarball filter error")

        def source_version_comparator(v1, v2):
            return org.wayround.utils.version.source_version_comparator(
                v1, v2,
                self.acceptable_source_name_extensions
                )

        filesl.sort(
            key=functools.cmp_to_key(
                source_version_comparator
                ),
            reverse=True
            )

        if resultmode == 'html':

            tarball_files = self.ui.tarballs_file_list(
                filesl,
                name,
                self._src_page_url
                )

            txt = self.ui.tarballs(
                name, tarball_files
                )

            ret = self.ui.html(
                title="Source Tarballs for package: '{}'".format(name),
                body=txt
                )

        elif resultmode == 'json':

            files = []
            for i in filesl:
                files.append("{}download{}".format(self._src_page_url, i))

            ret = json.dumps(files, sort_keys=True, indent=2)
            bottle.response.set_header('Content-Type', APPLICATION_JSON)

        return ret

    def search(self):

        decoded_params = bottle.request.params.decode('utf-8')

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

        name_list = self.pkg_repo_ctl.get_package_name_list()
        filtered_names = []

        for i in name_list:

            if not cs:
                i = i.lower()

            if (
                    (searchmode == 'filemask' and fnmatch.fnmatch(i, mask))
                    or (searchmode == 'regexp' and re.match(mask, i))
                    ):
                filtered_names.append(i)

        filtered_names.sort()

        ret = ''

        if resultmode == 'html':
            ret = self.ui.html(
                title="List of package names found by request mode "
                "`{}', using mask `{}' in `{}' mode".format(
                    searchmode_name,
                    mask,
                    cs_name
                    ),
                body=self.ui.search(searchmode=searchmode, mask=mask, cs=cs)
                +
                self.ui.search_result(lines=filtered_names)
                )

        elif resultmode == 'json':
            ret = json.dumps(filtered_names, sort_keys=True, indent=2)
            bottle.response.set_header('Content-Type', APPLICATION_JSON)

        return ret

    def name_by_name(self):

        decoded_params = bottle.request.params.decode('utf-8')

        if not 'tarball' in decoded_params:
            raise bottle.HTTPError(400, "Wrong tarball parameter")

        if not 'resultmode' in decoded_params:
            decoded_params['resultmode'] = 'html'

        if not decoded_params['resultmode'] in ['html', 'json']:
            raise bottle.HTTPError(400, "Wrong resultmode parameter")

        tarball = decoded_params['tarball']
        resultmode = decoded_params['resultmode']

        res = self.info_ctl.get_package_name_by_tarball_filename(
            tarball, mute=True
            )

        result_name = None
        if isinstance(res, list):
            result_name = res

        if result_name == None:
            raise bottle.HTTPError(404, "Not found")

        if resultmode == 'html':
            ret = self.ui.html(
                title="Result searching for package"
                " name by tarball name `{}'".format(tarball),
                body=self.ui.name_by_name(result=result_name)
                )

        elif resultmode == 'json':
            ret = json.dumps(result_name, sort_keys=True, indent=2)
            bottle.response.set_header('Content-Type', APPLICATION_JSON)

        return ret

    def bundles(self):

        decoded_params = bottle.request.params.decode('utf-8')

        if not 'resultmode' in decoded_params:
            decoded_params['resultmode'] = 'html'

        if not decoded_params['resultmode'] in ['html', 'json']:
            raise bottle.HTTPError(400, "Wrong resultmode parameter")

        resultmode = decoded_params['resultmode']

        filesl = self.bundles_ctl.list()
        filesl.sort(reverse=True)

        if resultmode == 'html':

            bundle_files = self.ui.bundles_file_list(filesl)

            txt = self.ui.bundles(
                bundle_files
                )

            ret = self.ui.html(
                title="Available bundles",
                body=txt
                )

        elif resultmode == 'json':

            ret = json.dumps(filesl, sort_keys=True, indent=2)
            bottle.response.set_header('Content-Type', APPLICATION_JSON)

        return ret

    def download_bundle(self, name):

        name = os.path.basename(name)

        ret = self.bundles_ctl.get(name)

        if ret == None:
            raise bottle.HTTPError(404, "Not Found")
        else:
            bottle.response.set_header('Content-Type', APPLICATION_JSON)

        return ret

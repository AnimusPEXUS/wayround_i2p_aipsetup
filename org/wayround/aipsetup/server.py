
import json
import os.path
import functools
import logging

import bottle

import org.wayround.aipsetup.serverui

TEXT_PLAIN = 'text/plain; codepage=utf-8'
APPLICATION_JSON = 'application/json; codepage=utf-8'


class AipsetupASPServer:

    def __init__(
        self,
        config,
        pkg_repo_ctl,
        info_ctl,
        tag_ctl
        ):

        web = os.path.join(os.path.dirname(__file__), 'web', 'pkg_server')

        templates_dir = os.path.join(web, 'templates')
        css_dir = os.path.join(web, 'css')
        js_dir = os.path.join(web, 'js')

        self.config = config

        self.host = config['web_server_config']['ip']
        self.port = config['web_server_config']['port']

        self.templates_dir = templates_dir
        self.css_dir = css_dir
        self.js_dir = js_dir

        self.pkg_repo_ctl = pkg_repo_ctl
        self.info_ctl = info_ctl
        self.tag_ctl = tag_ctl

        self.ui = org.wayround.aipsetup.serverui.UI(templates_dir)

        self.app = bottle.Bottle()

        self.app.route('/', 'GET', self.index)

        self.app.route('/js/<filename>', 'GET', self.js)
        self.app.route('/css/<filename>', 'GET', self.css)

        self.app.route('/category', 'GET', self.category_redirect)
        self.app.route('/category/', 'GET', self.category)
        self.app.route('/category/<path:path>', 'GET', self.category)
        self.app.route('/package/<name>', 'GET', self.package)

        self.app.route(
            '/package/<name>/asps/<name2>', 'GET', self.download_pkg
            )

        return

    def start(self):
        return bottle.run(self.app, host=self.host, port=self.port)

    def index(self):
        return ''

    def css(self, filename):
        return bottle.static_file(filename, root=self.css_dir)

    def js(self, filename):
        return bottle.static_file(filename, root=self.js_dir)

    def download_pkg(self, name, name2):

        base = os.path.basename(name2)

        path = self.pkg_repo_ctl.get_package_path_string(name)

        filename = org.wayround.utils.path.abspath(
            org.wayround.utils.path.join(
                self.config['package_repo']['dir'], path, 'pack', base
                )
            )

        if not filename.startswith(
            self.config['package_repo']['dir'] + os.path.sep
            ):
            raise bottle.HTTPError(404, "Wrong package name `{}'".format(name))

        if not os.path.isfile(filename):
            raise bottle.HTTPError(404, "File `{}' not found".format(base))

        logging.info("answering with file `{}'".format(filename))

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

        mode = None

        if not 'mode' in decoded_params:
            mode = 'html'
        else:
            mode = decoded_params['mode']
            if not mode in ['html', 'json']:
                raise bottle.HTTPError(400, "Invalid mode")

        ret = ''
        if mode == 'html':

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

            txt = self.ui.category(path, double_dot, categories, packages)

            ret = self.ui.html(
                title="Category: '{}'".format(path),
                body=txt
                )

        elif mode == 'json':

            if path == None:

                pkgs = self.pkg_repo_ctl.get_package_idname_dict(
                    None
                    )

                cats = self.pkg_repo_ctl.get_category_idname_dict(
                    None
                    )

            else:
                cid = self.pkg_repo_ctl.get_category_by_path(
                    path
                    )

                pkgs = self.pkg_repo_ctl.get_package_idname_dict(
                    cid
                    )

                cats = self.pkg_repo_ctl.get_category_idname_dict(
                    cid
                    )

            for i in list(pkgs.keys()):
                pkgs[i] = self.pkg_repo_ctl.get_package_path_string(
                    i
                    )

            for i in list(cats.keys()):
                cats[i] = self.pkg_repo_ctl.get_category_path_string(
                    i
                    )

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

    def package(self, name):

        decoded_params = bottle.request.params.decode('utf-8')

        mode = None

        ret = ''

        if not 'mode' in decoded_params:
            mode = 'normal'
        else:
            mode = decoded_params['mode']
            if not mode in ['normal', 'json']:
                raise bottle.HTTPError(400, "Invalid mode")

        if mode == 'normal':

            pkg_info = self.info_ctl.get_package_info_record(name)

            keys = set(
                org.wayround.aipsetup.info.SAMPLE_PACKAGE_INFO_STRUCTURE.keys()
                )

            rows = []

            for i in [
                'tags', 'name', 'description', 'basename', 'home_page',
                'newest_src', 'newest_pkg'
                ]:
                if i in keys:
                    keys.remove(i)

            for i in keys:
                rows.append(
                    (
                        '{}'.format(i.replace('_', ' ').capitalize()),
                        str(pkg_info[i])
                        )
                    )

            cid = self.pkg_repo_ctl.get_package_category_by_name(name)
            if cid != None:
                category = self.pkg_repo_ctl.get_category_path_string(cid)
            else:
                category = "< Package not indexed! >"

            tag_db = self.tag_ctl.tag_db
            tags = tag_db.get_tags(name)

            filesl = self.pkg_repo_ctl.get_package_files(name)
            filesl.sort(
                key=functools.cmp_to_key(
                    org.wayround.aipsetup.version.package_version_comparator
                    ),
                reverse=True
                )

            files = []
            for i in filesl:

                base = os.path.basename(i)

                stat = os.stat(
                    org.wayround.utils.path.join(
                        self.config['package_repo']['dir'],
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

            asp_files = self.ui.package_file_list(files, name)

            txt = self.ui.package(
                autorows=rows,
                basename=pkg_info['basename'],
                category=category,
                homepage=pkg_info['home_page'],
                description=pkg_info['description'],
                tags=tags,
                asp_list=asp_files,
                )

            ret = self.ui.html(
                title="Package: '{}'".format(name),
                body=txt
                )

        return ret


import json
import os.path

import bottle

import org.wayround.aipsetup.pkgindex
import org.wayround.aipsetup.pkglatest
import org.wayround.aipsetup.pkgtag
import org.wayround.aipsetup.pkginfo
import org.wayround.aipsetup.info

# imported in server_start_host()
#import org.wayround.aipsetup.serverui

TEXT_PLAIN = 'text/plain; codepage=utf-8'
APPLICATION_JSON = 'application/json; codepage=utf-8'


def cli_name():
    return 'server'

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

    import org.wayround.aipsetup.serverui

    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    css_dir = os.path.join(os.path.dirname(__file__), 'css')
    js_dir = os.path.join(os.path.dirname(__file__), 'js')

    app = AipsetupASPServer(
        templates_dir=templates_dir,
        css_dir=css_dir,
        js_dir=js_dir
        )

    app.start()

    return


class AipsetupASPServer:

    def __init__(
        self,
        host='localhost',
        port=8080,
        templates_dir='.',
        css_dir='./css',
        js_dir='./js'
        ):

        self.host = host
        self.port = port

        self.templates_dir = templates_dir
        self.css_dir = css_dir
        self.js_dir = js_dir

        self.ui = org.wayround.aipsetup.serverui.UI(templates_dir)

        self.app = bottle.Bottle()

        self.app.route('/', 'GET', self.index)

        self.app.route('/js/<filename>', 'GET', self.js)
        self.app.route('/css/<filename>', 'GET', self.css)

        self.app.route('/category', 'GET', self.category_redirect)
        self.app.route('/category/', 'GET', self.category)
        self.app.route('/category/<path:path>', 'GET', self.category)
        self.app.route('/package/<name>', 'GET', self.package)

        return

    def start(self):
        return bottle.run(self.app, host=self.host, port=self.port)

    def index(self):
        return ''

    def css(self, filename):
        return bottle.static_file(filename, root=self.css_dir)

    def js(self, filename):
        return bottle.static_file(filename, root=self.js_dir)

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

            cat_id = org.wayround.aipsetup.pkgindex.get_category_by_path(
                path
                )

            if cat_id == None:
                return bottle.HTTPError(404, "Category not found")

            double_dot = ''

            if cat_id != 0:

                parent_id = org.wayround.aipsetup.pkgindex.get_category_parent_by_id(
                    cat_id
                    )


                parent_path = org.wayround.aipsetup.pkgindex.get_category_path_string(
                    parent_id
                    )

                double_dot = self.ui.category_double_dot(parent_path)

            categories = []
            packages = []

            cats_ids = org.wayround.aipsetup.pkgindex.get_category_id_list(
                cat_id
                )

            pack_ids = org.wayround.aipsetup.pkgindex.get_package_id_list(
                cat_id
                )


            for i in cats_ids:
                categories.append(
                    {'path':
                        org.wayround.aipsetup.pkgindex.get_category_path_string(
                            i
                            ),
                     'name':org.wayround.aipsetup.pkgindex.get_category_by_id(
                            i
                            )
                    }
                )

            for i in pack_ids:
                packages.append(
                    org.wayround.aipsetup.pkgindex.get_package_by_id(
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

                pkgs = org.wayround.aipsetup.pkgindex.get_package_idname_dict(
                    None
                    )

                cats = org.wayround.aipsetup.pkgindex.get_category_idname_dict(
                    None
                    )

            else:
                cid = org.wayround.aipsetup.pkgindex.get_category_by_path(
                    path
                    )

                pkgs = org.wayround.aipsetup.pkgindex.get_package_idname_dict(
                    cid
                    )

                cats = org.wayround.aipsetup.pkgindex.get_category_idname_dict(
                    cid
                    )

            for i in list(pkgs.keys()):
                pkgs[i] = org.wayround.aipsetup.pkgindex.get_package_path_string(
                    i
                    )

            for i in list(cats.keys()):
                cats[i] = org.wayround.aipsetup.pkgindex.get_category_path_string(
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

            pkg_info = org.wayround.aipsetup.pkginfo.get_package_info_record(name)

            keys = set(org.wayround.aipsetup.info.SAMPLE_PACKAGE_INFO_STRUCTURE.keys())

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

            cid = org.wayround.aipsetup.pkgindex.get_package_category_by_name(name)
            if cid != None:
                category = org.wayround.aipsetup.pkgindex.get_category_path_string(cid)
            else:
                category = "< Package not indexed! >"


            latest_pkg = org.wayround.aipsetup.pkglatest.get_latest_pkg_from_record(
                name
                )

            latest_src = org.wayround.aipsetup.pkglatest.get_latest_src_from_record(
                name
                )

            latest_asp_basename = 'None'
            if latest_pkg:
                latest_asp_basename = os.path.basename(latest_pkg)

            latest_src_basename = 'None'
            if latest_src:
                latest_src_basename = os.path.basename(latest_src)


            tag_db = org.wayround.aipsetup.pkgtag.package_tags_connection()
            tags = tag_db.get_tags(name)

            txt = self.ui.package(
                autorows=rows,
                basename=pkg_info['basename'],
                category=category,
                homepage=pkg_info['home_page'],
                description=pkg_info['description'],
                tags=tags,
                latest_asp_basename=latest_asp_basename,
                latest_src_basename=latest_src_basename,
                asp_list='',
                tarball_list=''
                )

            ret = self.ui.html(
                title="Package: '{}'".format(name),
                body=txt
                )

        return ret


import os.path

import wayround_org.utils.path

import mako.template


class UI:

    def __init__(self, templates_dir):

        self.templates = {}

        for i in [
            'html',
            'index',
            'category',
            'asps',
            'asps_file_list',
            'tarballs',
            'tarballs_file_list',
            'bundles',
            'bundles_file_list',
            'category_double_dot',
            'package',
            'search',
            'search_result',
            'name_by_name'
            ]:
            self.templates[i] = mako.template.Template(
                filename=wayround_org.utils.path.join(templates_dir, i + '.html'),
                format_exceptions=False
                )

    def html(self, title, body):
        return self.templates['html'].render(
            title=title,
            body=body,
            js=[],
            css=['default.css']
            )

    def index(self, search_form):
        return self.templates['index'].render(
            search_form=search_form
            )

    def category(self, category_path, double_dot, categories, packages):

        return self.templates['category'].render(
            category_path=category_path,
            double_dot=double_dot,
            categories=categories,
            packages=packages
            )

    def category_double_dot(self, parent_path):

        return self.templates['category_double_dot'].render(
            parent_path=parent_path
            )

    def package(
        self,
        name,
        autorows,
        category,
        description,
        tags,
        src_page_url
        ):

        return self.templates['package'].render(
            name=name,
            autorows=autorows,
            category=category,
            description=description,
            tags=tags,
            src_page_url=src_page_url
            )

    def asps_file_list(self, files, pkg_name):
        return self.templates['asps_file_list'].render(
            files=files,
            pkg_name=pkg_name
            )

    def asps(self, name, asp_list):
        return self.templates['asps'].render(
            name=name,
            asp_list=asp_list
            )

    def tarballs_file_list(self, files, pkg_name, src_page_url):
        return self.templates['tarballs_file_list'].render(
            files=files,
            pkg_name=pkg_name,
            src_page_url=src_page_url
            )

    def tarballs(self, name, files_list):
        return self.templates['tarballs'].render(
            name=name,
            files_list=files_list
            )

    def snapshot_file_list(self, files):
        return self.templates['snapshot_file_list'].render(
            files=files
            )

    def snapshots(self, files_list):
        return self.templates['snapshots'].render(
            files_list=files_list
            )

    def search(self, searchmode='filemask', mask='*', cs=True):
        return self.templates['search'].render(
            searchmode=searchmode, mask=mask, cs=cs
            )

    def search_result(self, lines):
        return self.templates['search_result'].render(
            lines=lines
            )

    def name_by_name(self, result):
        return self.templates['name_by_name'].render(
            result=result
            )

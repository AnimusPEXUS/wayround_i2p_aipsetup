
import os.path
import logging
import time
import functools
import urllib.parse

import mako.template


import org.wayround.utils.path
import org.wayround.utils.mako_filters



class UI:

    def __init__(self, templates_dir):

        self.templates = {}

        for i in [
            'category',

#            'page_index',
#            'page_package',
#
            'package_file_list',
#            'package_sources_file_list',
#            'package_info',

            'category_double_dot',

            'package',

            'html'
            ]:
            self.templates[i] = mako.template.Template(
                filename=os.path.join(templates_dir, i + '.html')
                )

    def html(self, title, body):
        return self.templates['html'].render(
            title=title,
            body=body,
            js=[],
            css=['default.css']
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

    def package_file_list(self, files, pkg_name):

        return self.templates['package_file_list'].render(
            files=files,
            pkg_name=pkg_name
            )

    def package(
        self,
        autorows,
        basename,
        category,
        homepage,
        description,
        tags,
        asp_list
        ):

        return self.templates['package'].render(
            autorows=autorows,
            basename=basename,
            category=category,
            homepage=homepage,
            description=description,
            tags=tags,
            asp_list=asp_list,
            )


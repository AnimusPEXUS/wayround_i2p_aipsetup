#!/usr/bin/python3

import os.path

from setuptools import setup

setup(
    name='aipsetup',
    version='3.0.124',
    description='software tools for building and maintaining own gnu+linux distro',
    author='Alexey V Gorshkov',
    author_email='animus@wayround.org',
    url='https://github.com/AnimusPEXUS/org_wayround_aipsetup',
    packages=[
        'org.wayround.aipsetup',
        'org.wayround.aipsetup.buildtools',
        'org.wayround.aipsetup.gui'
        ],
    scripts=['aipsetup3.py'],
    install_requires=[
        'org_wayround_utils',
        'certdata',
        'sqlalchemy',
        'bottle',
        'mako'
        ],
    package_data={
        'org.wayround.aipsetup': [
            os.path.join('distro', '*.tar.xz'),
            os.path.join('gui', '*.glade'),
            os.path.join('distro', '*.json'),
            os.path.join('distro', '*.sqlite'),
            os.path.join('distro', 'pkg_buildscripts', '*.py'),
            os.path.join('distro', 'pkg_info', '*.json'),
            os.path.join('distro', 'groups', '*.json'),
            os.path.join('web', 'src_server', 'templates', '*'),
            os.path.join('web', 'src_server', 'js', '*'),
            os.path.join('web', 'src_server', 'css', '*'),
            os.path.join('web', 'pkg_server', 'templates', '*'),
            os.path.join('web', 'pkg_server', 'js', '*'),
            os.path.join('web', 'pkg_server', 'css', '*'),
            ],
        }
    )

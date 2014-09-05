#!/usr/bin/python3

import os.path

from distutils.core import setup

setup(
    name='aipsetup',
    version='3.0.115',
    description='software tools for building and maintaining own gnu+linux distro',
    author='Alexey V Gorshkov',
    author_email='animus@wayround.org',
    url='https://github.com/AnimusPEXUS/org_wayround_xmpp',
    packages=[
        'org.wayround.aipsetup',
        'org.wayround.aipsetup.buildtools',
        ],
    scripts=['aipsetup3.py'],
    install_requires=['org_wayround_utils'],
    package_data={
        'org.wayround.aipsetup': [
            os.path.join('ui', '*'),
            os.path.join('distro', '*.tar.xz'),
            os.path.join('distro', '*.json'),
            os.path.join('distro', '*.sqlite'),
            os.path.join('distro', 'pkg_buildscripts', '*.py'),
            os.path.join('distro', 'pkg_info', '*.json'),
            os.path.join('distro', 'groups', '*.json'),
            os.path.join('web', 'src_server', 'templates', '*.html')
            ],
        }
    )

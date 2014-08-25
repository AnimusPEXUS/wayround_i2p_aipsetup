#!/usr/bin/python3

import os.path

from distutils.core import setup

setup(
    name='aipsetup',
    version='3.0.114',
    description='aipsetup software packaging system',
    author='Alexey V Gorshkov',
    author_email='animus@wayround.org',
    url='http://wiki.wayround.org/soft/aipsetup',
    packages=[
        'org.wayround.aipsetup',
        'org.wayround.aipsetup.buildtools',
        ],
    scripts=['aipsetup3.py'],
    package_data={
        'org.wayround.aipsetup': [
            os.path.join('ui', '*'),
            os.path.join('distro', '*.py'),
            os.path.join('distro', '*.json'),
            os.path.join('distro', '*.sqlite'),
            os.path.join('distro', 'pkg_buildscripts', '*.py'),
            os.path.join('distro', 'pkg_info', '*.json'),
            os.path.join('web', 'src_server', 'templates', '*.html')
            ],
        }
    )

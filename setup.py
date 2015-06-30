#!/usr/bin/python3

import os.path

from setuptools import setup

setup(
    name='aipsetup',
    version='3.2.7',
    description='software tools for building and maintaining own gnu+linux distro',
    author='Alexey V Gorshkov',
    author_email='animus@wayround.org',
    url='https://github.com/AnimusPEXUS/wayround_org_aipsetup',
    packages=[
        'wayround_org.aipsetup',
        'wayround_org.aipsetup.buildtools',
        'wayround_org.aipsetup.gui',
        'wayround_org.aipsetup.builder_scripts'
        ],
    scripts=['aipsetup3.py'],
    install_requires=[
        'wayround_org_utils>=1.8.0',
        'certdata',
        'sqlalchemy',
        'bottle',
        'mako'
        ],
    package_data={
        'wayround_org.aipsetup': [
            os.path.join('*.sh'),
            os.path.join('distro', '*.tar.xz'),
            os.path.join('gui', '*.glade'),
            os.path.join('distro', '*.json'),
            os.path.join('distro', '*.sqlite'),
            os.path.join('distro', 'pkg_info', '*.json'),
            os.path.join('distro', 'pkg_groups', '*'),
            os.path.join('web', 'src_server', 'templates', '*'),
            os.path.join('web', 'src_server', 'js', '*'),
            os.path.join('web', 'src_server', 'css', '*'),
            os.path.join('web', 'pkg_server', 'templates', '*'),
            os.path.join('web', 'pkg_server', 'js', '*'),
            os.path.join('web', 'pkg_server', 'css', '*'),
            ],
        },
    entry_points={
        'console_scripts': 'aipsetup = wayround_org.aipsetup.main'
        }
    )

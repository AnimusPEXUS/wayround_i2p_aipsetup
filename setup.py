#!/usr/bin/python3

import os.path
import wayround_org.utils.path

from setuptools import setup

setup(
    name='aipsetup',
    version='3.3.9',
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
    # scripts=['aipsetup3.py'],
    install_requires=[
        'wayround_org_utils>=1.9.1',
        'certdata',
        'sqlalchemy',
        'bottle',
        'mako'
        ],
    package_data={
        'wayround_org.aipsetup': [
            wayround_org.utils.path.join('*.sh'),
            wayround_org.utils.path.join('gui', '*.glade'),
            wayround_org.utils.path.join('distro', '*.json'),
            wayround_org.utils.path.join('distro', '*.sqlite'),
            wayround_org.utils.path.join('distro', 'pkg_info', '*.json'),
            wayround_org.utils.path.join('distro', 'pkg_groups', '*'),
            wayround_org.utils.path.join('distro', 'etc', '*.tar.xz'),
            wayround_org.utils.path.join('web', 'src_server', 'templates', '*'),
            wayround_org.utils.path.join('web', 'src_server', 'js', '*'),
            wayround_org.utils.path.join('web', 'src_server', 'css', '*'),
            wayround_org.utils.path.join('web', 'pkg_server', 'templates', '*'),
            wayround_org.utils.path.join('web', 'pkg_server', 'js', '*'),
            wayround_org.utils.path.join('web', 'pkg_server', 'css', '*'),
            ],
        },
    entry_points={
        'console_scripts': 'aipsetup = wayround_org.aipsetup.main'
        }
    )

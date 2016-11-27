#!/usr/bin/python3

import os.path
import wayround_i2p.utils.path

from setuptools import setup

setup(
    name='aipsetup',
    version='3.4.5',
    description='software tools for building and maintaining own gnu+linux distro',
    author='Alexey V Gorshkov',
    author_email='animus@wayround.org',
    url='https://github.com/AnimusPEXUS/wayround_i2p_aipsetup',
    packages=[
        'wayround_i2p.aipsetup',
        'wayround_i2p.aipsetup.buildtools',
        'wayround_i2p.aipsetup.gui',
        'wayround_i2p.aipsetup.builder_scripts'
        ],
    # scripts=['aipsetup3.py'],
    install_requires=[
        'wayround_i2p_utils>=1.9.1',
        'certdata',
        'sqlalchemy',
        'bottle',
        'mako'
        ],
    package_data={
        'wayround_i2p.aipsetup': [
            wayround_i2p.utils.path.join('*.sh'),
            wayround_i2p.utils.path.join('gui', '*.glade'),
            wayround_i2p.utils.path.join('distro', '*.json'),
            wayround_i2p.utils.path.join('distro', '*.sqlite'),
            wayround_i2p.utils.path.join('distro', 'pkg_info', '*.json'),
            wayround_i2p.utils.path.join('distro', 'pkg_groups', '*'),
            wayround_i2p.utils.path.join('distro', 'etc', '*.tar.xz'),
            wayround_i2p.utils.path.join('web', 'src_server', 'templates', '*'),
            wayround_i2p.utils.path.join('web', 'src_server', 'js', '*'),
            wayround_i2p.utils.path.join('web', 'src_server', 'css', '*'),
            wayround_i2p.utils.path.join('web', 'pkg_server', 'templates', '*'),
            wayround_i2p.utils.path.join('web', 'pkg_server', 'js', '*'),
            wayround_i2p.utils.path.join('web', 'pkg_server', 'css', '*'),
            ],
        },
    entry_points={
        'console_scripts': 'aipsetup = wayround_i2p.aipsetup.main:main'
        }
    )

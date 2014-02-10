#!/usr/bin/python

import os.path

from distutils.core import setup

setup(
    name='aipsetup',
    version='3.0.107',
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
        'org.wayround.aipsetup':[
            os.path.join('ui', '*'),
            os.path.join('unicorn_distro', '*.py'),
            os.path.join('unicorn_distro', '*.json'),
            os.path.join('unicorn_distro', '*.sqlite'),
            os.path.join('unicorn_distro', 'pkg_buildscripts', '*.py'),
            os.path.join('unicorn_distro', 'pkg_info', '*.json'),
            ],
        }
    )

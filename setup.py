#!/usr/bin/python

from distutils.core import setup

setup(name='aipsetup',
      version='3.0a',
      description='aipsetup software packaging system',
      author='Alexey V Gorshkov',
      author_email='animus@wayround.org',
      url='http://wiki.wayround.org/soft/aipsetup',
      packages=['wayroundaipsetup'],
      scripts=['aipsetup3']
      )

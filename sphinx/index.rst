.. aipsetup documentation master file, created by
   sphinx-quickstart on Sat Jan 12 23:50:25 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to aipsetup's documentation!
====================================

aipsetup consists of several modules.

aipsetup is full circle desidgen for maintaining GNU/Linux distribution.

aipsetup can create packages.

aipsetup can install and remove packages.

aipsetup can distribute packages and self.


Modules
=======

All module names are relative to org.wayround.aipsetup package


* Package building modules

 * :mod:`buildscript <org.wayround.aipsetup.buildscript>`

 * :mod:`buildingsite <org.wayround.aipsetup.buildingsite>`

 * :mod:`build <org.wayround.aipsetup.build>`

 * :mod:`pack <org.wayround.aipsetup.pack>`

 * Building functions from othe modues:

  * :func:`package.build() <org.wayround.aipsetup.package.build>`

  * :func:`package.complete() <org.wayround.aipsetup.package.complete>`

* Package Installing and Uninstalling modules

 * :mod:`package <org.wayround.aipsetup.package>`

 * :mod:`pkgsnapshot <org.wayround.aipsetup.pkgsnapshot>` - installation 
   environment snapshots
   
* Other package tools:
  
  * :mod:`pkgdeps <org.wayround.aipsetup.pkgdeps>`
  
  * :mod:`pkgindex <org.wayround.aipsetup.pkgindex>` index sources, maintain 
    repository

* Modules for serving and getting packages

 * :mod:`server <org.wayround.aipsetup.server>`

  * :mod:`serverui <org.wayround.aipsetup.serverui>` - server UI module

 * :mod:`client <org.wayround.aipsetup.client>`

* GNU/Linux system tools:

 * :mod:`docbook <org.wayround.aipsetup.docbook>` - automated docbook 
   schemas installed

 * :mod:`clean <org.wayround.aipsetup.clean>` - system and aipsetup internals 
   cleaning utilities

* Configuration

 * :mod:`config <org.wayround.aipsetup.config>` - aipsetup config tools

 * :mod:`constitution <org.wayround.aipsetup.constitution>` - host, build, 
   target

* Package info related modules

 * :mod:`info <org.wayround.aipsetup.info>` - module to work with package info 
   files on disk

 * :mod:`name <org.wayround.aipsetup.name>` - package name parsing functions

 * :mod:`pkginfo <org.wayround.aipsetup.pkginfo>` - package info related 
   functions
   
 * :mod:`pkglatest <org.wayround.aipsetup.pkglatest>` - control on information 
   about latest source tarballs or latest asp packages

 * :mod:`pkgtag <org.wayround.aipsetup.pkgtag>` - packages tagging functionality

 * Editors

  * :mod:`infoeditor <org.wayround.aipsetup.infoeditor>` - edit package info on 
    disk and update pkginfo database

  * :mod:`latesteditor <org.wayround.aipsetup.latesteditor>` - latests pacakges 
    editor
    

* aipsetup internals:

 * :mod:`dbconnections <org.wayround.aipsetup.dbconnections>` - aipsetup global 
   database connector

 * :mod:`gtk <org.wayround.aipsetup.gtk>` - aipsetup global gtk connection 	 

 * :mod:`help <org.wayround.aipsetup.help>` - aipsetup help system 	 
 	
 * :mod:`repoman <org.wayround.aipsetup.repoman>` - gathering aipsetup CLI 
   interface for 
   :mod:`pkgindex <org.wayround.aipsetup.pkgindex>`,
   :mod:`pkginfo <org.wayround.aipsetup.pkginfo>`,
   :mod:`pkglatest <org.wayround.aipsetup.pkglatest>` 
   and 
   :mod:`pkgtag <org.wayround.aipsetup.pkgtag>` 
   modules
  	 
 	


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


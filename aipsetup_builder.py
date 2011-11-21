#!/usr/bin/python
# -*- coding: utf-8 -*-

import os.path
import os
import re
import aipsetup_utils
import shutil


class Builder:
    """This class is for all building methods.

    It is initiated with some dir, which may be not a working, but this class
    must be able to check that dir, init it if required, Copy source there And
    use pointed themplate for source building.

    !! Packaging and downloading routines must be on other classes !!"""

    DIR_TARBALL  = '00.TARBALL'
    DIR_TEMPLATE = '01.TEMPLATE'
    DIR_SOURCE   = '02.SOURCE'
    DIR_PATCH    = '03.PATCH'
    DIR_BUILD    = '04.BUILD'
    DIR_FS_ROOT  = '05.FS_ROOT'
    DIR_LOGS     = '06.LOGS'
    DIR_LISTS    = '07.LISTS'
    DIR_PACKAGE  = '08.PACKAGE'


    directory = ''

    def __init__(self, directory):
        self.directory = directory

    def isWdDirRestricted(self):
        """This function is a rutine to check supplied dir is it suitable to be
        a working dir"""

        dirs_begining_with = [
            '/bin', '/boot' , '/daemons',
            '/dev', '/etc', '/lib', '/proc' ,
            '/sbin', '/sys',
            '/usr/bin', '/usr/sbin', '/usr/lib',
            '/usr/man', '/usr/share'
        ]

        exec_dirs = ['/opt', '/usr', '/var', '/']

        dir_str_abs = os.path.abspath(self.directory)

        for i in dirs_begining_with:
            if (re.match('^'+i, dir_str_abs) != None):
                return True

        for i in exec_dirs:
            if i == dir_str_abs:
                return True

        return False

    def init(self):
        """Initiates pointed dir for farver usage. All contents is removed"""

        # Commented it out. I fink it's not needed in class
        # if self.isWdDirRestricted(self.directory):
            # print '-e- ' + dir_str + ' is restricted working dir'
            # print '    won\'t init'
            # return -1

        # if exists and not derictory - not continue
        if ((os.path.exists(self.directory))
            and not os.path.isdir(self.directory)):
            return -2

        # ensure directory exists
        if (not os.path.exists(self.directory)):
            os.makedirs(self.directory)

        # remove all files and directories in initiating dir
        if (os.path.exists(self.directory)) and os.path.isdir(self.directory):
            files = os.listdir(self.directory)
            for i in files:
                tfile = pathRemoveDblSlash(self.directory+'/'+i)
                if (os.path.isdir(tfile)):
                    shutil.rmtree(tfile)
                    continue
                os.unlink(tfile)

        # create all subdirs
        # NOTE: probebly '/' in paths is not a problem, couse we
        #       working with GNU/Linux (maby other UNIXes) only
        try:
            os.makedirs(aipsetup_utils.pathRemoveDblSlash(
                self.directory+'/'+self.DIR_TARBALL))

            os.makedirs(aipsetup_utils.pathRemoveDblSlash(
                self.directory+'/'+self.DIR_TEMPLATE))

            os.makedirs(aipsetup_utils.pathRemoveDblSlash(
                self.directory+'/'+self.DIR_SOURCE))

            os.makedirs(aipsetup_utils.pathRemoveDblSlash(
                self.directory+'/'+self.DIR_PATCH))

            os.makedirs(aipsetup_utils.pathRemoveDblSlash(
                self.directory+'/'+self.DIR_BUILD))

            os.makedirs(aipsetup_utils.pathRemoveDblSlash(
                self.directory+'/'+self.DIR_FS_ROOT))

            os.makedirs(aipsetup_utils.pathRemoveDblSlash(
                self.directory+'/'+self.DIR_LOGS))

            os.makedirs(aipsetup_utils.pathRemoveDblSlash(
                self.directory+'/'+self.DIR_LISTS))

            os.makedirs(aipsetup_utils.pathRemoveDblSlash(
                self.directory+'/'+self.DIR_PACKAGE))
        except:
            print '-e- error creating working dir tree'
            return -3

        return 0

    def cp(self, filename):
        '''This method copyes pointed file to 00.TARBALL directory'''

        src_file_base_name = os.path.basename(filename);

        shutil.copy(filename,
                    self.directory + '/' + self.DIR_TARBALL + '/' + src_file_base_name)

        return

    def person(self, template):
        '''Personalize working directory

        Simply copyes template to working dir'''

        if not os.path.isfile(aipsetup_config['templates'] + '/' + template):
            print '-e- This template not found in ' + aipsetup_config['templates']
            return False

        try:
            shutil.copy(aipsetup_config['templates'] + '/' + template,
                       self.directory + '/' + self.DIR_TEMPLATE + '/' + template)
        except:
            print '-e- Some template copying error'
            return False

        return True

    def e_src(self):
        '''Clean extracted source dir and extract fresh source there'''

        sources_dir = self.directory+'/'+self.DIR_SOURCE

        if ((os.path.exists(sources_dir))
            and os.path.isdir(sources_dir)):
            files = os.listdir(sources_dir)
            for i in files:
                tfile = pathRemoveDblSlash(self.directory+'/'+i)
                if (os.path.isdir(tfile)):
                    shutil.rmtree(tfile)
                    continue
                os.unlink(tfile)

# -*- coding: utf-8 -*-

import os
import sys

import aipsetup
import aipsetup.buildingsite
import aipsetup.utils.time
import aipsetup.utils.text
import aipsetup.utils.error

class Log:

    def __init__(self, config, building_site, logname):

        ret = 0
        self.code = 0
        self.fileobj = None
        self.logname = logname

        log_dir = aipsetup.buildingsite.getDir_BUILD_LOGS(
            building_site
            )

        if not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir)
            except:
                print("-e- Exception while creating building logs dir")
                aipsetup.utils.error.print_exception_info(
                    sys.exc_info()
                    )
                ret = 1
        else:

            if not os.path.isdir(log_dir) \
                    or os.path.islink(log_dir):
                print("-e- Current file type is not acceptable: %(name)s" % {
                    'name': log_dir
                    })
                ret = 2

        if ret == 0:
            timestamp = aipsetup.utils.time.currenttime_stamp()
            filename = os.path.abspath(
                os.path.join(
                    log_dir,
                    "%(ts)s-%(name)s.txt" % {
                        'ts': timestamp,
                        'name': logname
                        }
                    )
                )
            try:
                self.fileobj = open(filename, 'w')
            except:
                print("-e- Error opening log file")
                aipsetup.utils.error.print_exception_info(sys.exc_info())
                ret = 3
            else:
                print((
                    "[%(ts)s] =///////= Starting `%(name)s' log =///////=\n") % {
                        'ts': timestamp,
                        'name': self.logname
                        })
                self.fileobj.write(
                    "[%(ts)s] =///////= Starting `%(name)s' log =///////=\n" % {
                        'ts': timestamp,
                        'name': self.logname
                    }
                    )

        if ret != 0:
            raise Exception

        return

    def stop(self):
        if self.fileobj == None:
            raise Exception

        timestamp = aipsetup.utils.time.currenttime_stamp()
        print("[%(ts)s] =///////= Stopping `%(name)s' log =///////=\n" % {
            'ts': timestamp,
            'name': self.logname
            })
        self.fileobj.write("[%(ts)s] =///////= Stopping `%(name)s' log =///////=\n" % {
                'ts': timestamp,
                'name': self.logname
                })
        self.fileobj.flush()
        self.fileobj.close()
        return

    def write(self, text, echo=True):
        if self.fileobj == None:
            raise Exception

        timestamp = aipsetup.utils.time.currenttime_stamp()
        if echo:
            print("[%(ts)s] %(text)s" % {
                'ts': timestamp,
                'text': aipsetup.utils.text.deunicodify(text)
                })
        self.fileobj.write("[%(ts)s] %(text)s\n" % {
                'ts': timestamp,
                'text': aipsetup.utils.text.deunicodify(text)
                })
        return


    def __del__(self):
        if not self.fileobj.closed:
            try:
                self.stop()
            except:
                pass



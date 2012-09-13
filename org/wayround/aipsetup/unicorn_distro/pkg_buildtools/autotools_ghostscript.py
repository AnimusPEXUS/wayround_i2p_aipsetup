
import os.path
import subprocess
import glob
import shutil
import sys

import org.wayround.aipsetup.buildingsite
import org.wayround.utils.osutils
import org.wayround.utils.archive

def export_functions():
    return {
        'build': build,
        'distribute': distribute,
        }

def determine_source_dir(buildingsite, pkginfo):

    source_dir = os.path.abspath(
        os.path.join(
            buildingsite,
            org.wayround.aipsetup.buildingsite.DIR_SOURCE,
            pkginfo['pkg_buildinfo']['autotools_configure_opts']['config_dir']
            )
        )

    return source_dir

def determine_building_dir(buildingsite, source_dir, pkginfo):
    building_dir = ''

    if pkginfo['pkg_buildinfo']['autotools_configure_opts']['separate_build_dir'] == True:

        building_dir = os.path.abspath(
            os.path.join(
                buildingsite,
                org.wayround.aipsetup.buildingsite.DIR_BUILDING,
                pkginfo['pkg_buildinfo']['autotools_configure_opts']['config_dir']
                )
            )

    else:

        building_dir = source_dir

    return building_dir


def determine_builder_parameters(pkginfo):

    run_parameters = []

    for i in pkginfo['pkg_buildinfo']['autotools_build_params']:
        if pkginfo['pkg_buildinfo']['autotools_build_params'][i] != None:
            run_parameters.append("%(par_name)s=%(par_value)s" % {
                    'par_name': i,
                    'par_value': pkginfo['pkg_buildinfo']['autotools_build_params'][i]
                    })
        else:
            run_parameters.append("%(par_name)s" % {
                    'par_name': i
                    })

    return run_parameters


def determine_installer_parameters(pkginfo):

    run_parameters = []

    for i in pkginfo['pkg_buildinfo']['autotools_distribute_params']:
        if pkginfo['pkg_buildinfo']['autotools_distribute_params'][i] != None:
            run_parameters.append("%(par_name)s=%(par_value)s" % {
                    'par_name': i,
                    'par_value': pkginfo['pkg_buildinfo']['autotools_distribute_params'][i]
                    })
        else:
            run_parameters.append("%(par_name)s" % {
                    'par_name': i
                    })

    return run_parameters



def build(log, buildingsite='.'):

    ret = 0

    pi = org.wayround.aipsetup.buildingsite.read_package_info(
        buildingsite, ret_on_error=None)

    if pi == None:
        log.error("error getting information about package")
        ret = 101
    else:

        source_dir = determine_source_dir(
            buildingsite, pi
            )

        building_dir = determine_building_dir(
            buildingsite, source_dir, pi
            )

        run_parameters = determine_builder_parameters(
            pi
            )

        makefile = os.path.abspath(
            os.path.join(
                building_dir,
                pi['pkg_buildinfo']['autotools_build_opts']['make_file_name']
                )
            )

        cmd = ['make'] + ['-f', makefile] + run_parameters

        log.info("Starting autotools make script with following command:")
        log.write("    %(cmd)s" % {
                'cmd': repr(cmd)
                })
        log.write("-i-")

        env = org.wayround.utils.osutils.env_vars_edit(
            pi['pkg_buildinfo']['autotools_build_envs'],
            pi['pkg_buildinfo']['autotools_build_env_opts']['mode']
            )

        if len(pi['pkg_buildinfo']['autotools_build_envs']) > 0:
            log.info("Environment Modifications: %(list)s" % {
                    'list': ' '.join(repr(i) for i in pi['pkg_buildinfo']['autotools_build_envs'])
                    })

        p = None
        try:
            p = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=building_dir)
        except:
            log.error("exception while starting make script")
            log.write("    command line was:")
            log.write("    " + repr(cmd))
            log.write(
                org.wayround.utils.error.return_exception_info(
                    sys.exc_info()
                    )
                )
            ret = 100

        else:

            t = org.wayround.utils.stream.lbl_write(
                p.stdout,
                log,
                True
                )
            t.start()

            t2 = org.wayround.utils.stream.lbl_write(
                p.stderr,
                log,
                True,
                typ='error'
                )
            t2.start()
            t.join()
            t2.join()

            try:
                p.wait()
            except:
                log.write("\n-e- exception oqured while waiting for builder")
                log.write(
                    org.wayround.utils.error.return_exception_info(
                        sys.exc_info()
                        )
                    )
                ret = 100
            else:
                log.info("builder return code was: %(code)d" % {
                        'code': p.returncode
                        })

                ret = p.returncode

                if ret == 0:

                    cmd = ['make'] + ['-f', makefile] + ['so'] + run_parameters

                    log.info("Starting autotools make script with following command:")
                    log.write("    %(cmd)s" % {
                            'cmd': repr(cmd)
                            })
                    log.write("-i-")

                    env = org.wayround.utils.osutils.env_vars_edit(
                        pi['pkg_buildinfo']['autotools_build_envs'],
                        pi['pkg_buildinfo']['autotools_build_env_opts']['mode']
                        )

                    if len(pi['pkg_buildinfo']['autotools_build_envs']) > 0:
                        log.info("Environment Modifications: %(list)s" % {
                                'list': ' '.join(repr(i) for i in pi['pkg_buildinfo']['autotools_build_envs'])
                                })

                    p = None
                    try:
                        p = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=building_dir)
                    except:
                        log.error("exception while starting make script")
                        log.write("    command line was:")
                        log.write("    " + repr(cmd))
                        log.write(
                            org.wayround.utils.error.return_exception_info(
                                sys.exc_info()
                                )
                            )
                        ret = 100

                    else:

                        t = org.wayround.utils.stream.lbl_write(
                            p.stdout,
                            log,
                            True
                            )
                        t.start()

                        t2 = org.wayround.utils.stream.lbl_write(
                            p.stderr,
                            log,
                            True,
                            typ='error'
                            )
                        t2.start()
                        t.join()
                        t2.join()

                        try:
                            p.wait()
                        except:
                            log.write("\n-e- exception oqured while waiting for builder")
                            log.write(
                                org.wayround.utils.error.return_exception_info(
                                    sys.exc_info()
                                    )
                                )
                            ret = 100
                        else:
                            log.info("builder return code was: %(code)d" % {
                                    'code': p.returncode
                                    })
                            ret = p.returncode

    return ret


def distribute(log, buildingsite='.'):

    ret = 0

    pi = org.wayround.aipsetup.buildingsite.read_package_info(
        buildingsite, ret_on_error=None)

    if pi == None:
        log.error("error getting information about package")
        ret = 101
    else:

        source_dir = determine_source_dir(
            buildingsite, pi
            )

        building_dir = determine_building_dir(
            buildingsite, source_dir, pi
            )

        run_parameters = determine_installer_parameters(
            pi
            )

        makefile = os.path.abspath(
            os.path.join(
                building_dir,
                pi['pkg_buildinfo']['autotools_distribute_opts']['make_file_name']
                )
            )

        destdir = os.path.abspath(
            os.path.join(
                buildingsite,
                org.wayround.aipsetup.buildingsite.DIR_DESTDIR
                )
            )

        if not os.path.isdir(destdir):
            os.makedirs(destdir)

        cmd = ['make'] + ['-f', makefile] + run_parameters \
            + ['install'] + ['%(dd_name)s=%(dd)s' % {
            'dd':destdir,
            'dd_name': pi['pkg_buildinfo']['autotools_distribute_opts']['DESTDIR_opt_name']
            }]

        log.info("Starting autotools install script with following command:")
        log.write("    %(cmd)s" % {
                'cmd': repr(cmd)
                })
        log.write("-i-")

        env = org.wayround.utils.osutils.env_vars_edit(
            pi['pkg_buildinfo']['autotools_distribute_envs'],
            pi['pkg_buildinfo']['autotools_distribute_env_opts']['mode']
            )

        if len(pi['pkg_buildinfo']['autotools_distribute_envs']) > 0:
            log.write(
                "-i- Environment Modifications: %(list)s" % {
                    'list': ' '.join(
                        repr(i) \
                            for i in pi['pkg_buildinfo']['autotools_distribute_envs']
                        )
                    }
                )

        p = None
        try:
            p = subprocess.Popen(
                cmd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=building_dir
                )
        except:
            log.error(
                "exception while starting install script\n" +
                "    command line was:\n" +
                "    " + repr(cmd) +
                org.wayround.utils.error.return_exception_info(
                    sys.exc_info()
                    )
                )
            ret = 100

        else:

            t = org.wayround.utils.stream.lbl_write(
                p.stdout,
                log,
                True
                )
            t.start()

            t2 = org.wayround.utils.stream.lbl_write(
                p.stderr,
                log,
                True,
                typ='error'
                )
            t2.start()
            t.join()
            t2.join()

            try:
                p.wait()
            except:
                log.write("\n-e- exception oqured while waiting for installer")
                log.write(
                    org.wayround.utils.error.return_exception_info(
                        sys.exc_info()
                        )
                    )
                ret = 100
            else:
                log.info("installer return code was: %(code)d" % {
                        'code': p.returncode
                        })

                ret = p.returncode

                if ret == 0:

                    cmd = ['make'] + ['-f', makefile] + run_parameters \
                        + ['soinstall'] + ['%(dd_name)s=%(dd)s' % {
                        'dd':destdir,
                        'dd_name': pi['pkg_buildinfo']['autotools_distribute_opts']['DESTDIR_opt_name']
                        }]

                    log.info("Starting autotools install script with following command:")
                    log.write("    %(cmd)s" % {
                            'cmd': repr(cmd)
                            })
                    log.write("-i-")

                    env = org.wayround.utils.osutils.env_vars_edit(
                        pi['pkg_buildinfo']['autotools_distribute_envs'],
                        pi['pkg_buildinfo']['autotools_distribute_env_opts']['mode']
                        )

                    if len(pi['pkg_buildinfo']['autotools_distribute_envs']) > 0:
                        log.write(
                            "-i- Environment Modifications: %(list)s" % {
                                'list': ' '.join(
                                    repr(i) \
                                        for i in pi['pkg_buildinfo']['autotools_distribute_envs']
                                    )
                                }
                            )

                    p = None
                    try:
                        p = subprocess.Popen(
                            cmd,
                            env=env,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            cwd=building_dir
                            )
                    except:
                        log.error(
                            "exception while starting install script\n" +
                            "    command line was:\n" +
                            "    " + repr(cmd) +
                            org.wayround.utils.error.return_exception_info(
                                sys.exc_info()
                                )
                            )
                        ret = 100

                    else:

                        t = org.wayround.utils.stream.lbl_write(
                            p.stdout,
                            log,
                            True
                            )
                        t.start()

                        t2 = org.wayround.utils.stream.lbl_write(
                            p.stderr,
                            log,
                            True,
                            typ='error'
                            )
                        t2.start()
                        t.join()
                        t2.join()

                        try:
                            p.wait()
                        except:
                            log.write("\n-e- exception oqured while waiting for installer")
                            log.write(
                                org.wayround.utils.error.return_exception_info(
                                    sys.exc_info()
                                    )
                                )
                            ret = 100
                        else:
                            log.info("installer return code was: %(code)d" % {
                                    'code': p.returncode
                                    })

                            ret = p.returncode

    return ret


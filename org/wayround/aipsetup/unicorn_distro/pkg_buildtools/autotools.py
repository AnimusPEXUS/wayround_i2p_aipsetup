
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
        'extract': extract,
        'configure': configure,
        'make': build
        }

def determine_source_dir(buildingsite, info):

    source_dir = os.path.abspath(
        os.path.join(
            buildingsite,
            org.wayround.aipsetup.buildingsite.DIR_SOURCE,
            info['data']['settings']['config_dir']
            )
        )

    return source_dir

def determine_building_dir(buildingsite, source_dir, info):
    building_dir = ''

    if info['data']['settings']['separate_build_dir'] == True:

        building_dir = os.path.abspath(
            os.path.join(
                buildingsite,
                org.wayround.aipsetup.buildingsite.DIR_BUILDING,
                info['data']['settings']['config_dir']
                )
            )

    else:

        building_dir = source_dir

    return building_dir

def determine_configure_parameters(info):

    run_parameters = []

    for i in info['data']['opts']:
        if info['data']['opts'][i] != None:
            run_parameters.append(
                "--%(par_name)s=%(par_value)s" % {
                    'par_name': i,
                    'par_value': info['data']['opts'][i]
                    }
                )
        else:
            run_parameters.append(
                "--%(par_name)s" % {
                    'par_name': i
                    }
                )

    return run_parameters


def determine_make_parameters(pkginfo):

    run_parameters = []

    for i in pkginfo['data']['autotools_build_params']:
        if pkginfo['data']['autotools_build_params'][i] != None:
            run_parameters.append("%(par_name)s=%(par_value)s" % {
                    'par_name': i,
                    'par_value': pkginfo['data']['autotools_build_params'][i]
                    })
        else:
            run_parameters.append("%(par_name)s" % {
                    'par_name': i
                    })

    return run_parameters


def determine_installer_parameters(pkginfo):

    run_parameters = []

    for i in pkginfo['pkg_buildscript']['autotools_distribute_params']:
        if pkginfo['pkg_buildscript']['autotools_distribute_params'][i] != None:
            run_parameters.append("%(par_name)s=%(par_value)s" % {
                    'par_name': i,
                    'par_value': pkginfo['pkg_buildscript']['autotools_distribute_params'][i]
                    })
        else:
            run_parameters.append("%(par_name)s" % {
                    'par_name': i
                    })

    return run_parameters


def extract(buildingsite='.', info=None):

    ret = 0

    log = org.wayround.utils.log.Log(
        org.wayround.aipsetup.buildingsite.getDIR_BUILD_LOGS(buildingsite),
        info['name']
        )

    tarball_dir = os.path.join(
        buildingsite,
        org.wayround.aipsetup.buildingsite.DIR_TARBALL
        )

    output_dir = os.path.join(
        buildingsite,
        org.wayround.aipsetup.buildingsite.DIR_SOURCE
        )

    if os.path.isdir(output_dir):
        log.info("cleaningup source dir")
        org.wayround.utils.file.cleanup_dir(output_dir)

    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    arch = glob.glob(os.path.join(tarball_dir, '*'))
    if len(arch) == 0:
        log.error("No tarballs supplied")
        ret = 1
    elif len(arch) > 1:
        log.error("autotools[configurer]: too many source files")
        ret = 2
    else:

        arch = arch[0]

        log.info("Extracting {}".format(os.path.basename(arch)))
        extr_error = org.wayround.utils.archive.extract(
            arch, output_dir
            )

        if extr_error != 0:
            log.error("Extraction error: %(num)d" % {
                    'num': extr_error
                })
            ret = 3
        else:

            extracted_dir = glob.glob(os.path.join(output_dir, '*'))

            if len(extracted_dir) > 1:
                log.error("autotools['extract']: too many extracted files")
                ret = 4
            else:
                extracted_dir = extracted_dir[0]
                extracted_dir_files = glob.glob(os.path.join(extracted_dir, '*'))
                for i in extracted_dir_files:
                    shutil.move(i, output_dir)
                shutil.rmtree(extracted_dir)

    log.stop()

    return ret


def configure(buildingsite='.', info=None):

    ret = 0

    log = org.wayround.utils.log.Log(
        org.wayround.aipsetup.buildingsite.getDIR_BUILD_LOGS(buildingsite),
        info['name']
        )

    source_dir = determine_source_dir(
        buildingsite, info
        )

    building_dir = determine_building_dir(
        buildingsite, source_dir, info
        )

#        if os.path.isdir(building_dir):
#            log.info("cleaningup building dir")
#            org.wayround.utils.file.cleanup_dir(building_dir)

    if not os.path.isdir(building_dir):
        os.makedirs(building_dir)

    run_parameters = determine_configure_parameters(
        info
        )

    config_script = os.path.abspath(
        os.path.join(
            source_dir,
            info['data']['settings']['script_name']
            )
        )

    cmd = ['bash'] + [config_script] + run_parameters

    log.info("Working directory: {}".format(building_dir))

    log.info(
        "Starting autotools configurer script with following command:\n"
        "    %(cmd)s" % {
            'cmd': repr(cmd)
            }
        )

    env = org.wayround.utils.osutils.env_vars_edit(
        info['data']['env'],
        info['data']['env_opts']['mode']
        )

    if len(info['data']['env']) > 0:
        log.info("Environment Modifications: %(list)s" % {
                'list': ' '.join(repr(i) for i in info['data']['env'])
                })

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
            "exception while starting configuration script"
            "    command line was:"
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
            log.write("\n-e- exception oqured while waiting for configure")
            log.write(
                org.wayround.utils.error.return_exception_info(
                    sys.exc_info()
                    )
                )
            ret = 100
        else:
            log.info("configurer return code was: %(code)d" % {
                    'code': p.returncode
                    })
            ret = p.returncode

    log.stop()

    return ret

def build(log, buildingsite='.'):

    ret = 0

    info = org.wayround.aipsetup.buildingsite.read_package_info(
        buildingsite, ret_on_error=None)

    if info == None:
        log.error("error getting information about package")
        ret = 101
    else:

        source_dir = determine_source_dir(
            buildingsite, info
            )

        building_dir = determine_building_dir(
            buildingsite, source_dir, info
            )

        run_parameters = determine_builder_parameters(
            info
            )

        makefile = os.path.abspath(
            os.path.join(
                building_dir,
                info['pkg_buildscript']['autotools_build_opts']['make_file_name']
                )
            )

        cmd = ['make'] + ['-f', makefile] + run_parameters

        log.info("Starting autotools make script with following command:")
        log.write("    %(cmd)s" % {
                'cmd': repr(cmd)
                })
        log.write("-i-")

        env = org.wayround.utils.osutils.env_vars_edit(
            info['pkg_buildscript']['autotools_build_envs'],
            info['pkg_buildscript']['autotools_build_env_opts']['mode']
            )

        if len(info['pkg_buildscript']['autotools_build_envs']) > 0:
            log.info("Environment Modifications: %(list)s" % {
                    'list': ' '.join(repr(i) for i in info['pkg_buildscript']['autotools_build_envs'])
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

    info = org.wayround.aipsetup.buildingsite.read_package_info(
        buildingsite, ret_on_error=None)

    if info == None:
        log.error("error getting information about package")
        ret = 101
    else:

        source_dir = determine_source_dir(
            buildingsite, info
            )

        building_dir = determine_building_dir(
            buildingsite, source_dir, info
            )

        run_parameters = determine_installer_parameters(
            info
            )

        makefile = os.path.abspath(
            os.path.join(
                building_dir,
                info['pkg_buildscript']['autotools_distribute_opts']['make_file_name']
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
            'dd_name': info['pkg_buildscript']['autotools_distribute_opts']['DESTDIR_opt_name']
            }]

        log.info("Starting autotools install script with following command:")
        log.write("    %(cmd)s" % {
                'cmd': repr(cmd)
                })
        log.write("-i-")

        env = org.wayround.utils.osutils.env_vars_edit(
            info['pkg_buildscript']['autotools_distribute_envs'],
            info['pkg_buildscript']['autotools_distribute_env_opts']['mode']
            )

        if len(info['pkg_buildscript']['autotools_distribute_envs']) > 0:
            log.write(
                "-i- Environment Modifications: %(list)s" % {
                    'list': ' '.join(
                        repr(i) \
                            for i in info['pkg_buildscript']['autotools_distribute_envs']
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


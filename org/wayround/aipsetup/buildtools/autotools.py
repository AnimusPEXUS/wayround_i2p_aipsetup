
"""
autotools tools and specific to it
"""

import os.path
import subprocess
import glob
import shutil
import sys
import tempfile

import org.wayround.aipsetup.buildingsite
import org.wayround.utils.osutils
import org.wayround.utils.archive

def determine_configure_dir(buildingsite, info):
    """
    Determine config dir taking in account info['data']['settings']['config_dir']
    """

    config_dir = os.path.abspath(
        org.wayround.aipsetup.buildingsite.getDIR_SOURCE(
            buildingsite
            ) + os.path.sep + info['data']['settings']['config_dir']
        )

    return config_dir

def determine_building_dir(buildingsite, source_dir, info):
    """
    Determine building dir taking in account info['data']['settings']['separate_build_dir']
    """

    building_dir = ''

    if info['data']['settings']['separate_build_dir'] == True:

        building_dir = os.path.abspath(
            org.wayround.aipsetup.buildingsite.getDIR_BUILDING(
                buildingsite
                )
#            + os.path.sep + info['data']['settings']['config_dir']                                       
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


def extract(
    log,
    buildingsite,
    tarball,
    outdir,
    unwrap_dir=False,
    rename_dir=False
    ):

    ret = 0

    if os.path.isdir(outdir):
        log.info("cleaningup source dir")
        org.wayround.utils.file.cleanup_dir(outdir)

    if not os.path.isdir(outdir):
        os.makedirs(outdir)

    tmpdir = tempfile.mkdtemp(
        dir=org.wayround.aipsetup.buildingsite.getDIR_TEMP(buildingsite)
        )

    if not os.path.isdir(tmpdir):
        os.makedirs(tmpdir)


    log.info("Extracting {}".format(os.path.basename(tarball)))
    extr_error = org.wayround.utils.archive.extract(
        tarball, tmpdir
        )

    if extr_error != 0:
        log.error(
            "Extraction error: {}".format(extr_error)
            )
        ret = 3
    else:

        extracted_dir = os.listdir(tmpdir)

        if len(extracted_dir) > 1:
            log.error("too many extracted files")
            ret = 4
        else:

            extracted_dir = tmpdir + os.path.sep + extracted_dir[0]

            if unwrap_dir:

                extracted_dir_files = os.listdir(extracted_dir)
                for i in extracted_dir_files:
                    shutil.move(extracted_dir + os.path.sep + i, outdir)
                shutil.rmtree(extracted_dir)

            else:
                if rename_dir:
                    shutil.move(extracted_dir, outdir + os.path.sep + str(rename_dir))
                else:
                    shutil.move(extracted_dir, outdir)

    return ret


def configure(
    log,
    buildingsite,
    opts,
    separate_build=True,
    env=None,
    env_mode='copy',
    config_dir='.',
    script_name='configure'
    ):

    ret = 0

    buildingsite = os.path.abspath(buildingsite)

    log = org.wayround.utils.log.Log(
        org.wayround.aipsetup.buildingsite.getDIR_BUILD_LOGS(buildingsite),
        info['name']
        )

    source_dir = determine_configure_dir(
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

def make(log, buildingsite='.'):

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


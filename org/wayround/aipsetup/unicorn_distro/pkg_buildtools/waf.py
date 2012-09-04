
import os.path
import sys
import subprocess


import org.wayround.utils.osutils
import org.wayround.utils.error
import org.wayround.utils.stream

import org.wayround.aipsetup.buildingsite

def export_functions():
    return {
        'configure': configure,
        'build': build,
        'distribute': distribute,
        }


def determine_source_dir(buildingsite, pkginfo):

    source_dir = os.path.abspath(
        os.path.join(
            buildingsite,
            org.wayround.aipsetup.buildingsite.DIR_SOURCE,
            pkginfo['pkg_buildinfo']['waf_configure_opts']['config_dir']
            )
        )

    return source_dir

def determine_building_dir(buildingsite, source_dir, pkginfo):
    building_dir = ''

    if pkginfo['pkg_buildinfo']['waf_configure_opts']['separate_build_dir'] == True:

        building_dir = os.path.abspath(
            os.path.join(
                buildingsite,
                org.wayround.aipsetup.buildingsite.DIR_BUILDING,
                pkginfo['pkg_buildinfo']['waf_configure_opts']['config_dir']
                )
            )

    else:

        building_dir = source_dir

    return building_dir

def determine_configurer_parameters(pkginfo):

    run_parameters = []

    for i in pkginfo['pkg_buildinfo']['waf_configure_params']:
        if pkginfo['pkg_buildinfo']['waf_configure_params'][i] != None:
            run_parameters.append("--%(par_name)s=%(par_value)s" % {
                    'par_name': i,
                    'par_value': pkginfo['pkg_buildinfo']['waf_configure_params'][i]
                    })
        else:
            run_parameters.append("--%(par_name)s" % {
                    'par_name': i
                    })

    return run_parameters


def determine_builder_parameters(pkginfo):

    run_parameters = []

    for i in pkginfo['pkg_buildinfo']['waf_build_params']:
        if pkginfo['pkg_buildinfo']['waf_build_params'][i] != None:
            run_parameters.append("%(par_name)s=%(par_value)s" % {
                    'par_name': i,
                    'par_value': pkginfo['pkg_buildinfo']['waf_build_params'][i]
                    })
        else:
            run_parameters.append("%(par_name)s" % {
                    'par_name': i
                    })

    return run_parameters


def determine_installer_parameters(pkginfo):

    run_parameters = []

    for i in pkginfo['pkg_buildinfo']['waf_distribute_params']:
        if pkginfo['pkg_buildinfo']['waf_distribute_params'][i] != None:
            run_parameters.append("%(par_name)s=%(par_value)s" % {
                    'par_name': i,
                    'par_value': pkginfo['pkg_buildinfo']['waf_distribute_params'][i]
                    })
        else:
            run_parameters.append("%(par_name)s" % {
                    'par_name': i
                    })

    return run_parameters

def _overal(log, buildingsite='.', name='configure'):

    ret = 0

    if not name in ['distribute', 'build', 'configure']:
        raise ValueError("Wrong `name' parameter")

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

        destdir = os.path.abspath(
            os.path.join(
                buildingsite,
                org.wayround.aipsetup.buildingsite.DIR_DESTDIR
                )
            )

        if not os.path.isdir(building_dir):
            os.makedirs(building_dir)

        run_parameters = determine_configurer_parameters(
            pi
            )

        config_script = os.path.abspath(
            os.path.join(
                source_dir,
                pi['pkg_buildinfo']['waf_configure_opts']['script_name']
                )
            )

        command = ''
        if name == 'distribute':
            command = 'install'
        else:
            command = name

        cmd = ['python3'] + [config_script] + [command] + run_parameters

        if name == 'distribute':
            cmd.append('--destdir=' + destdir)

        log.info("Working directory: {}".format(building_dir))
        log.info(
            "Starting waf configurer script with following command:\n"
            "    {}".format(
                repr(cmd)
                )
            )

        env = org.wayround.utils.osutils.env_vars_edit(
            pi['pkg_buildinfo']['waf_configure_envs'],
            pi['pkg_buildinfo']['waf_configure_env_opts']['mode']
            )

        if len(pi['pkg_buildinfo']['waf_configure_envs']) > 0:
            log.info("Environment Modifications: %(list)s" % {
                    'list': ' '.join(repr(i) for i in pi['pkg_buildinfo']['waf_configure_envs'])
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
                log.error(
                    "exception occurred while waiting for waf\n" +
                    org.wayround.utils.error.return_exception_info(
                        sys.exc_info()
                        )
                    )
                ret = 100
            else:
                log.info("waf return code was: %(code)d" % {
                        'code': p.returncode
                        })
                ret = p.returncode

    return ret

def configure(log, buildingsite='.'):
    return _overal(log, buildingsite='.', name='configure')

def build(log, buildingsite='.'):
    return _overal(log, buildingsite='.', name='build')

def distribute(log, buildingsite='.'):
    return _overal(log, buildingsite='.', name='distribute')

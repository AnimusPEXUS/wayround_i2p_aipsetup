import os
import os.path
import subprocess
import glob
import shutil
import sys

import aipsetup.extractor
import aipsetup.buildingsite
import aipsetup.utils
# import aipsetup.name


def determine_source_dir(config, buildingsite, pkginfo):

    source_dir = os.path.abspath(
        os.path.join(
            buildingsite,
            aipsetup.buildingsite.DIR_SOURCE,
            pkginfo['pkg_buildinfo']['autotools_configure_opts']['config_dir']
            )
        )

    return source_dir

def determine_building_dir(config, buildingsite, source_dir, pkginfo):
    building_dir = ''

    if pkginfo['pkg_buildinfo']['autotools_configure_opts']['separate_build_dir'] == True:

        building_dir = os.path.abspath(
            os.path.join(
                buildingsite,
                aipsetup.buildingsite.DIR_BUILDING,
                pkginfo['pkg_buildinfo']['autotools_configure_opts']['config_dir']
                )
            )

    else:

        building_dir = source_dir

    return building_dir

def determine_configurer_parameters(config, pkginfo):

    run_parameters = []

    for i in pkginfo['pkg_buildinfo']['autotools_configure_params']:
        if pkginfo['pkg_buildinfo']['autotools_configure_params'][i] != None:
            run_parameters.append("--%(par_name)s=%(par_value)s" % {
                    'par_name': i,
                    'par_value': pkginfo['pkg_buildinfo']['autotools_configure_params'][i]
                    })
        else:
            run_parameters.append("--%(par_name)s" % {
                    'par_name': i
                    })

    return run_parameters


def determine_builder_parameters(config, pkginfo):

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


def determine_installer_parameters(config, pkginfo):

    run_parameters = []

    for i in pkginfo['pkg_buildinfo']['autotools_install_params']:
        if pkginfo['pkg_buildinfo']['autotools_install_params'][i] != None:
            run_parameters.append("%(par_name)s=%(par_value)s" % {
                    'par_name': i,
                    'par_value': pkginfo['pkg_buildinfo']['autotools_install_params'][i]
                    })
        else:
            run_parameters.append("%(par_name)s" % {
                    'par_name': i
                    })

    return run_parameters


def extract(config, buildingsite='.'):
    tarball_dir = os.path.join(
        buildingsite,
        aipsetup.buildingsite.DIR_TARBALL
        )

    output_dir = os.path.join(
        buildingsite,
        aipsetup.buildingsite.DIR_SOURCE
        )

    if os.path.isdir(output_dir):
        print "-i- cleaningup source dir"
        aipsetup.utils.cleanup_dir(output_dir)

    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    arch = glob.glob(os.path.join(tarball_dir, '*'))
    if len(arch) == 0:
        print "-e- No tarballs supplied"
    elif len(arch) > 1:
        print "-e- autotools[configurer]: too many source files"
    else:

        arch = arch[0]

        arch_bn = os.path.basename(arch)

        aipsetup.extractor.extract(arch, output_dir)

        extracted_dir = glob.glob(os.path.join(output_dir, '*'))

        if len(extracted_dir) > 1:
            print "-e- autotools[configurer]: too many extracted files"
        else:
            extracted_dir = extracted_dir[0]
            extracted_dir_files = glob.glob(os.path.join(extracted_dir, '*'))
            for i in extracted_dir_files:
                shutil.move(i, output_dir)
            shutil.rmtree(extracted_dir)

    return


def configure(config, buildingsite='.'):

    ret = 0

    pi = aipsetup.buildingsite.read_package_info(
        config, buildingsite, ret_on_error=None)

    if pi == None:
        print "-e- error getting information about package"
    else:

        source_dir = determine_source_dir(
            config, buildingsite, pi
            )

        building_dir = determine_building_dir(
            config, buildingsite, source_dir, pi
            )

        if not os.path.isdir(building_dir):
            os.makedirs(building_dir)

        run_parameters = determine_configurer_parameters(
            config, pi
            )

        config_script = os.path.abspath(
            os.path.join(
                source_dir,
                pi['pkg_buildinfo']['autotools_configure_opts']['script_name']
                )
            )

        cmd = ['bash'] + [config_script] + run_parameters

        print "-i- Starting autotools configurer script with following command:"
        print "    %(cmd)s" % {
            'cmd': repr(cmd)
            }
        print "-i-"

        env = aipsetup.utils.env_vars_edit(
            pi['pkg_buildinfo']['autotools_configure_envs'],
            pi['pkg_buildinfo']['autotools_configure_env_opts']['mode']
            )

        if len(pi['pkg_buildinfo']['autotools_configure_envs']) > 0:
            print "-i- Environment Modifications: %(list)s" % {
                'list': ' '.join(repr(i) for i in pi['pkg_buildinfo']['autotools_configure_envs'])
                }

        p = None
        try:
            p = subprocess.Popen(cmd, env=env, cwd=building_dir)
        except:
            print "-e- exception while starting configuration script"
            print "    command line was:"
            print "    " + repr(cmd)
            aipsetup.utils.print_exception_info(sys.exc_info())
            ret = 100

        else:

            try:
                p.wait()
            except:
                print "\n-e- exception oqured while waiting for configure"
                aipsetup.utils.print_exception_info(sys.exc_info())
                ret = 100
            else:
                print "-i- configurer return code was: %(code)d" % {
                    'code': p.returncode
                    }
                ret = p.returncode

    return ret

def build(config, buildingsite='.'):

    ret = 0

    pi = aipsetup.buildingsite.read_package_info(
        config, buildingsite, ret_on_error=None)

    if pi == None:
        print "-e- error getting information about package"
    else:

        source_dir = determine_source_dir(
            config, buildingsite, pi
            )

        building_dir = determine_building_dir(
            config, buildingsite, source_dir, pi
            )

        run_parameters = determine_builder_parameters(
            config, pi
            )

        makefile = os.path.abspath(
            os.path.join(
                building_dir,
                pi['pkg_buildinfo']['autotools_build_opts']['make_file_name']
                )
            )

        cmd = ['make'] + ['-f', makefile] + run_parameters

        print "-i- Starting autotools make script with following command:"
        print "    %(cmd)s" % {
            'cmd': repr(cmd)
            }
        print "-i-"

        env = aipsetup.utils.env_vars_edit(
            pi['pkg_buildinfo']['autotools_build_envs'],
            pi['pkg_buildinfo']['autotools_build_env_opts']['mode']
            )

        if len(pi['pkg_buildinfo']['autotools_build_envs']) > 0:
            print "-i- Environment Modifications: %(list)s" % {
                'list': ' '.join(repr(i) for i in pi['pkg_buildinfo']['autotools_build_envs'])
                }

        p = None
        try:
            p = subprocess.Popen(cmd, env=env, cwd=building_dir)
        except:
            print "-e- exception while starting make script"
            print "    command line was:"
            print "    " + repr(cmd)
            aipsetup.utils.print_exception_info(sys.exc_info())
            ret = 100

        else:

            try:
                p.wait()
            except:
                print "\n-e- exception oqured while waiting for builder"
                aipsetup.utils.print_exception_info(sys.exc_info())
                ret = 100
            else:
                print "-i- builder return code was: %(code)d" % {
                    'code': p.returncode
                    }
                ret = p.returncode

    return ret


def install(config, buildingsite='.'):

    ret = 0

    pi = aipsetup.buildingsite.read_package_info(
        config, buildingsite, ret_on_error=None)

    if pi == None:
        print "-e- error getting information about package"
    else:

        source_dir = determine_source_dir(
            config, buildingsite, pi
            )

        building_dir = determine_building_dir(
            config, buildingsite, source_dir, pi
            )

        run_parameters = determine_installer_parameters(
            config, pi
            )

        makefile = os.path.abspath(
            os.path.join(
                building_dir,
                pi['pkg_buildinfo']['autotools_install_opts']['make_file_name']
                )
            )

        destdir = os.path.abspath(
            os.path.join(
                buildingsite,
                aipsetup.buildingsite.DIR_DESTDIR
                )
            )

        if not os.path.isdir(destdir):
            os.makedirs(destdir)

        cmd = ['make'] + ['-f', makefile] + run_parameters + ['install'] + ['DESTDIR=%(dd)s' % {'dd':destdir}]

        print "-i- Starting autotools install script with following command:"
        print "    %(cmd)s" % {
            'cmd': repr(cmd)
            }
        print "-i-"

        env = aipsetup.utils.env_vars_edit(
            pi['pkg_buildinfo']['autotools_install_envs'],
            pi['pkg_buildinfo']['autotools_install_env_opts']['mode']
            )

        if len(pi['pkg_buildinfo']['autotools_install_envs']) > 0:
            print "-i- Environment Modifications: %(list)s" % {
                'list': ' '.join(repr(i) for i in pi['pkg_buildinfo']['autotools_install_envs'])
                }

        p = None
        try:
            p = subprocess.Popen(cmd, env=env, cwd=building_dir)
        except:
            print "-e- exception while starting install script"
            print "    command line was:"
            print "    " + repr(cmd)
            aipsetup.utils.print_exception_info(sys.exc_info())
            ret = 100

        else:

            try:
                p.wait()
            except:
                print "\n-e- exception oqured while waiting for installer"
                aipsetup.utils.print_exception_info(sys.exc_info())
                ret = 100
            else:
                print "-i- installer return code was: %(code)d" % {
                    'code': p.returncode
                    }
                ret = p.returncode

    return ret

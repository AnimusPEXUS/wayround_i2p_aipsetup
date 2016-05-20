
"""
cmake tools and specific to it
"""

import os.path
import subprocess
import pprint
import sys

import wayround_org.aipsetup.build
import wayround_org.utils.error
import wayround_org.utils.log
import wayround_org.utils.osutils
import wayround_org.utils.path


def calc_conf_hbt_options(builder_obj):

    #host = builder_obj.host
    #build = builder_obj.build
    #target = builder_obj.target

    ret = []

    #if host is not None:
    #    ret.append('-DCMAKE_C_COMPILER={}-gcc'.format(host))
    #    ret.append('-DCMAKE_CXX_COMPILER={}-g++'.format(host))

    # TODO: provide equivalent for --target and --build options

    # if build is not None:
    #    ret.append('--build=' + build)

    # if target is not None:
    #    ret.append('--target=' + target)

    return ret


def determine_abs_configure_dir(buildingsite, config_dir):
    """
    Determine config dir taking in account config_dir
    """

    config_dir = wayround_org.utils.path.abspath(
        wayround_org.aipsetup.build.getDIR_SOURCE(
            buildingsite
            ) + os.path.sep + config_dir
        )

    return config_dir


def determine_building_dir(
        buildingsite, config_dir, separate_build_dir
        ):
    """
    Determine building dir taking in account config_dir and separate_build_dir
    """

    building_dir = ''

    if separate_build_dir == True:

        building_dir = wayround_org.utils.path.abspath(
            wayround_org.aipsetup.build.getDIR_BUILDING(
                buildingsite
                )
            )
    else:
        building_dir = wayround_org.utils.path.abspath(
            wayround_org.utils.path.join(
                wayround_org.aipsetup.build.getDIR_SOURCE(buildingsite),
                config_dir
                )
            )

    return building_dir


def cmake_high(
        building_site,
        options,
        arguments,
        environment,
        environment_mode,
        source_subdir,
        build_in_separate_dir,
        log=None,
        ):

    building_site = wayround_org.utils.path.abspath(building_site)

    own_log = False
    if log is None:
        own_log = True
        log = wayround_org.utils.log.Log(
            wayround_org.aipsetup.build.getDIR_BUILD_LOGS(building_site),
            'cmake'
            )

    env = wayround_org.utils.osutils.env_vars_edit(
        environment,
        environment_mode
        )

    if len(environment) > 0:
        log.info(
            "Environment modifications:\n{}".format(
                pprint.pformat(environment)
                )
            )

    script_path = determine_abs_configure_dir(
        building_site,
        source_subdir
        )

    working_dir = determine_building_dir(
        building_site,
        source_subdir,
        build_in_separate_dir
        )

    ret = cmake_low(
        log=log,
        build_dir=working_dir,
        src_dir=script_path,
        working_dir=working_dir,
        opts=options,
        args=arguments,
        env=env
        )

    if own_log:
        # log.close()

    return ret


def cmake_low(
        log,
        build_dir,
        src_dir,
        working_dir,
        opts,
        args,
        env
        ):

    ret = 0

    cmd = ['cmake'] + opts + ['--build=' + build_dir] + args + [src_dir]

    log.info("directory: {}".format(working_dir))
    log.info("src: {}".format(src_dir))
    log.info("build dir: {}".format(build_dir))
    log.info("command:")
    for i in cmd:
        log.info("    {}".format(i))
    #log.info("command(joined): {}".format(' '.join(cmd)))

    p = None
    try:
        p = subprocess.Popen(
            cmd,
            env=env,
            stdout=log.stdout,
            stderr=log.stderr,
            cwd=working_dir
            )
    except:
        log.error(
            "exception while starting cmake\n"
            "    command line was:\n"
            "    " + repr(cmd) +
            wayround_org.utils.error.return_exception_info(
                sys.exc_info()
                )
            )
        ret = 100

    else:

        try:
            p.wait()
        except:
            log.error(
                "Exception occurred while waiting for cmake\n{}".format(
                    wayround_org.utils.error.return_exception_info(
                        sys.exc_info()
                        )
                    )
                )
            ret = 100
        else:
            tmp_s = "cmake return code was: {}".format(p.returncode)

            if p.returncode == 0:
                log.info(tmp_s)
            else:
                log.error(tmp_s)

            ret = p.returncode

    return ret

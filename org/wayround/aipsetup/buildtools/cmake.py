
"""
cmake tools and specific to it
"""

import os.path
import subprocess
import sys

import org.wayround.aipsetup.buildingsite
import org.wayround.utils.osutils
import org.wayround.utils.error

def determine_abs_configure_dir(buildingsite, config_dir):
    """
    Determine config dir taking in account config_dir
    """

    config_dir = os.path.abspath(
        org.wayround.aipsetup.buildingsite.getDIR_SOURCE(
            buildingsite
            ) + os.path.sep + config_dir
        )

    while r'//' in config_dir:
        config_dir.replace(r'//', '/')

    return config_dir

def determine_building_dir(
    buildingsite, config_dir, separate_build_dir
    ):
    """
    Determine building dir taking in account config_dir and separate_build_dir
    """

    building_dir = ''

    if separate_build_dir == True:

        building_dir = os.path.abspath(
            org.wayround.aipsetup.buildingsite.getDIR_BUILDING(
                buildingsite
                )
            )
    else:
        building_dir = (
            org.wayround.aipsetup.buildingsite.getDIR_SOURCE(buildingsite)
            + os.path.sep
            + config_dir
            )

    return building_dir


def cmake_high(
    building_site,
    options,
    arguments,
    environment,
    environment_mode,
    source_subdir,
    build_in_separate_dir
    ):

    ret = 0

    building_site = os.path.abspath(building_site)

    log = org.wayround.utils.log.Log(
        org.wayround.aipsetup.buildingsite.getDIR_BUILD_LOGS(
            building_site
            ),
        'cmake'
        )


    env = org.wayround.utils.osutils.env_vars_edit(
        environment,
        environment_mode
        )

    if len(environment) > 0:
        log.info(
            "Environment modifications: {}".format(
                repr(environment)
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

    log.close()

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
    log.info("command: {}".format(cmd))
    log.info("command(joined): {}".format(' '.join(cmd)))

    p = None
    try:
        p = subprocess.Popen(
            cmd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=working_dir
            )
    except:
        log.error(
            "exception while starting cmake\n"
            "    command line was:\n"
            "    " + repr(cmd) +
            org.wayround.utils.error.return_exception_info(
                sys.exc_info()
                )
            )
        ret = 100

    else:

        t1 = org.wayround.utils.stream.lbl_write(
            p.stdout,
            log,
            True
            )
        t1.start()

        t2 = org.wayround.utils.stream.lbl_write(
            p.stderr,
            log,
            True,
            typ='error'
            )
        t2.start()
        t1.join()
        t2.join()

        try:
            p.wait()
        except:
            log.error(
                "Exception occurred while waiting for cmake\n{}".format(
                    org.wayround.utils.error.return_exception_info(
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
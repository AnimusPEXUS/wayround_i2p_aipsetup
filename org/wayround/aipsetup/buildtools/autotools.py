
"""
autotools tools and specific to it
"""

import os.path
import subprocess
import sys
import tempfile

import org.wayround.aipsetup.build
import org.wayround.utils.archive
import org.wayround.utils.error
import org.wayround.utils.log
import org.wayround.utils.osutils
import org.wayround.utils.path
import org.wayround.utils.tarball


def determine_abs_configure_dir(buildingsite, config_dir):
    """
    Determine config dir taking in account config_dir
    """

    config_dir = org.wayround.utils.path.abspath(
        org.wayround.aipsetup.build.getDIR_SOURCE(
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

        building_dir = org.wayround.utils.path.abspath(
            org.wayround.aipsetup.build.getDIR_BUILDING(
                buildingsite
                )
            )
    else:
        building_dir = (
            org.wayround.aipsetup.build.getDIR_SOURCE(buildingsite)
            + os.path.sep
            + config_dir
            )

    return building_dir


def extract_high(
    building_site,
    tarball_basename,
    unwrap_dir,
    rename_dir,
    more_when_one_extracted_ok=False
    ):

    ret = 0

    building_site = org.wayround.utils.path.abspath(building_site)

    log = org.wayround.utils.log.Log(
        org.wayround.aipsetup.build.getDIR_BUILD_LOGS(building_site),
        'extract'
        )

    building_site = org.wayround.utils.path.abspath(building_site)

    tarball_dir = org.wayround.aipsetup.build.getDIR_TARBALL(building_site)

    source_dir = org.wayround.aipsetup.build.getDIR_SOURCE(building_site)

    tarball_dir_files = os.listdir(tarball_dir)

    tarball_dir_files_len = len(tarball_dir_files)

    tmpdir = tempfile.mkdtemp(
        dir=org.wayround.aipsetup.build.getDIR_TEMP(building_site)
        )

    if tarball_dir_files_len == 0:
        log.error("No Source Tarball Supplied")
        ret = 1
    else:

        tarball = None
        for i in tarball_dir_files:
            parsed = org.wayround.utils.tarball.parse_tarball_name(
                i, mute=True
                )
            if isinstance(parsed, dict):
                if parsed['groups']['name'] == tarball_basename:
                    tarball = tarball_dir + os.path.sep + i
                    break

        if not tarball:
            log.error(
                "Couldn't find acceptable tarball for current building site"
                )
            ret = 2
        else:

            ret = org.wayround.utils.archive.extract_low(
                log,
                tmpdir,
                tarball,
                source_dir,
                unwrap_dir=unwrap_dir,
                rename_dir=rename_dir,
                more_when_one_extracted_ok=more_when_one_extracted_ok
                )

    log.close()

    return ret


def configure_high(
    building_site,
    options,
    arguments,
    environment,
    environment_mode,
    source_configure_reldir,
    use_separate_buildding_dir,
    script_name,
    run_script_not_bash,
    relative_call
    ):
    """
    Start configuration script

    source_configure_reldir - relative path from source dir to configure dir;
    script_name - configure script name;
    run_script_not_bash - run {full_path}/configure, not
        bash {full_path}/configure;
    relative_call - make {full_path} bee '.'
    """

    ret = 0

    building_site = org.wayround.utils.path.abspath(building_site)

    log = org.wayround.utils.log.Log(
        org.wayround.aipsetup.build.getDIR_BUILD_LOGS(building_site),
        'configure'
        )

    pkg_info = \
        org.wayround.aipsetup.build.BuildingSiteCtl(building_site).\
            read_package_info()

    if not isinstance(pkg_info, dict):
        log.error("Can't read package info")
        ret = 1
    else:

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
            source_configure_reldir
            )

        working_dir = determine_building_dir(
            building_site,
            source_configure_reldir,
            use_separate_buildding_dir
            )

        ret = configure_low(
            log,
            script_path,
            working_dir,
            options,
            arguments,
            env,
            run_script_not_bash,
            relative_call,
            script_name
            )

    log.close()

    return ret


def configure_low(
    log,
    script_path,
    working_dir,
    opts,
    args,
    env,
    run_script_not_bash,
    relative_call,
    script_name
    ):

    ret = 0

    if relative_call:
        script_path = org.wayround.utils.path.relpath(script_path, working_dir)

    cmd = []
    if not run_script_not_bash:
        cmd = (['bash'] +
            [script_path + os.path.sep + script_name] +
            opts + args)
    else:
        cmd = [script_path + os.path.sep + script_name] + opts + args

    log.info("directory: {}".format(working_dir))
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
            "exception while starting configuration script\n"
            "    command line was:\n"
            "    " + repr(cmd) +
            org.wayround.utils.error.return_exception_info(
                sys.exc_info()
                )
            )
        ret = 100

    else:

        org.wayround.utils.log.process_output_logger(p, log)

        try:
            p.wait()
        except:
            log.error(
                "Exception occurred while waiting for configure\n" +
                org.wayround.utils.error.return_exception_info(
                    sys.exc_info()
                    )
                )
            ret = 100
        else:
            tmp_s = "configure return code was: {}".format(p.returncode)

            if p.returncode == 0:
                log.info(tmp_s)
            else:
                log.error(tmp_s)

            ret = p.returncode

    return ret


def make_high(
    building_site,
    options,
    arguments,
    environment,
    environment_mode,
    use_separate_buildding_dir,
    source_configure_reldir
    ):

    building_site = org.wayround.utils.path.abspath(building_site)

    log = org.wayround.utils.log.Log(
        org.wayround.aipsetup.build.getDIR_BUILD_LOGS(building_site),
        'make'
        )

    env = org.wayround.utils.osutils.env_vars_edit(
        environment,
        environment_mode
        )

    if len(environment) > 0:
        log.info(
            "Environment modifications: {}".format(
                repr(i) for i in list(environment.keys())
                )
            )

    working_dir = determine_building_dir(
        building_site,
        source_configure_reldir,
        use_separate_buildding_dir
        )

    ret = make_low(log, options, arguments, env, working_dir)

    log.close()

    return ret


def make_low(
    log,
    opts,
    args,
    env,
    working_dir
    ):

    ret = 0

    cmd = ['make'] + opts + args

    log.info("directory: {}".format(working_dir))
    log.info("command: {}".format(cmd))

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
            "exception while starting make script\n" +
            "    command line was:\n" +
            "    " + repr(cmd) + "\n" +
            org.wayround.utils.error.return_exception_info(
                sys.exc_info()
                )
            )
        ret = 100

    else:

        org.wayround.utils.log.process_output_logger(p, log)

        try:
            p.wait()
        except:
            log.error(
                "exception occurred while waiting for builder\n" +
                org.wayround.utils.error.return_exception_info(
                    sys.exc_info()
                    )
                )
            ret = 100
        else:
            tmp_s = "make return code was: {}".format(p.returncode)

            if p.returncode == 0:
                log.info(tmp_s)
            else:
                log.error(tmp_s)

            ret = p.returncode

    return ret


"""
autotools tools and specific to it
"""

import os.path
import subprocess
import sys
import tempfile

import wayround_org.aipsetup.build
import wayround_org.utils.archive
import wayround_org.utils.error
import wayround_org.utils.log
import wayround_org.utils.osutils
import wayround_org.utils.path
import wayround_org.utils.tarball


def calc_conf_hbt_options(builder_obj):

    host = builder_obj.host
    build = builder_obj.build
    target = builder_obj.target
    forced_target = builder_obj.forced_target

    if (host != None 
        and (
            (host == build == target)
            or
            ((host == build) and (target == None))
            )
        and not forced_target
        ):
        target = None

    ret = []

    if host is not None:
        ret.append('--host=' + host)

    if build is not None:
        ret.append('--build=' + build)

    if target is not None:
        ret.append('--target=' + target)

    return ret


def determine_abs_configure_dir(buildingsite, config_dir):
    """
    Determine config dir taking in account config_dir
    """

    config_dir = wayround_org.utils.path.join(
        wayround_org.utils.path.abspath(
            wayround_org.aipsetup.build.getDIR_SOURCE(
                buildingsite
                )
            ),
        config_dir
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
    elif isinstance(separate_build_dir, str):
        building_dir = wayround_org.utils.path.abspath(
            separate_build_dir
            )
    else:
        building_dir = (
            wayround_org.utils.path.join(
                wayround_org.aipsetup.build.getDIR_SOURCE(buildingsite),
                config_dir
                )
            )

    return building_dir


def extract_high(
        building_site,
        tarball_basename,
        unwrap_dir,
        rename_dir,
        more_when_one_extracted_ok=False,
        log=None
        ):

    building_site = wayround_org.utils.path.abspath(building_site)

    own_log = False
    if log is None:
        own_log = True
        log = wayround_org.utils.log.Log(
            wayround_org.aipsetup.build.getDIR_BUILD_LOGS(building_site),
            'extract'
            )

    ret = 0

    tarball_dir = wayround_org.aipsetup.build.getDIR_TARBALL(building_site)

    source_dir = wayround_org.aipsetup.build.getDIR_SOURCE(building_site)

    tarball_dir_files = os.listdir(tarball_dir)

    tarball_dir_files_len = len(tarball_dir_files)

    tmpdir = tempfile.mkdtemp(
        dir=wayround_org.aipsetup.build.getDIR_TEMP(building_site)
        )

    if tarball_dir_files_len == 0:
        log.error("No Source Tarball Supplied")
        ret = 1
    else:

        tarball = None
        for i in tarball_dir_files:
            parsed = wayround_org.utils.tarball.parse_tarball_name(
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

            ret = wayround_org.utils.archive.extract_low(
                log,
                tmpdir,
                tarball,
                source_dir,
                unwrap_dir=unwrap_dir,
                rename_dir=rename_dir,
                more_when_one_extracted_ok=more_when_one_extracted_ok
                )

    if own_log:
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
        relative_call,
        log=None
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

    building_site = wayround_org.utils.path.abspath(building_site)

    own_log = False
    if log is None:
        own_log = True
        log = wayround_org.utils.log.Log(
            wayround_org.aipsetup.build.getDIR_BUILD_LOGS(building_site),
            'configure'
            )

    pkg_info = \
        wayround_org.aipsetup.build.BuildingSiteCtl(building_site).\
        read_package_info()

    if not isinstance(pkg_info, dict):
        log.error("Can't read package info")
        ret = 1
    else:

        env = wayround_org.utils.osutils.env_vars_edit(
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

    if own_log:
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
        script_path = wayround_org.utils.path.relpath(script_path, working_dir)

    cmd = []
    if not run_script_not_bash:
        cmd = (['bash'] +
               [script_path + os.path.sep + script_name] +
               opts + args)
    else:
        cmd = [script_path + os.path.sep + script_name] + opts + args

    log.info("directory: {}".format(working_dir))
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
            "exception while starting configuration script\n"
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
                "Exception occurred while waiting for configure\n" +
                wayround_org.utils.error.return_exception_info(
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
        source_configure_reldir,
        log=None,
        make_filename=None
        ):

    building_site = wayround_org.utils.path.abspath(building_site)

    own_log = False
    if log is None:
        own_log = True
        log = wayround_org.utils.log.Log(
            wayround_org.aipsetup.build.getDIR_BUILD_LOGS(building_site),
            'make'
            )

    env = wayround_org.utils.osutils.env_vars_edit(
        environment,
        environment_mode
        )

    if len(environment) > 0:
        log.info(
            "Environment modifications: {}".format(
                repr(environment)
                )
            )

    working_dir = determine_building_dir(
        building_site,
        source_configure_reldir,
        use_separate_buildding_dir
        )

    ret = make_low(
        log,
        options,
        arguments,
        env,
        working_dir,
        make_filename=make_filename
        )

    if own_log:
        log.close()

    return ret


def make_low(
        log,
        opts,
        args,
        env,
        working_dir,
        make_filename=None
        ):

    ret = 0

    mfn = []
    if make_filename is not None:
        mfn = ['-f', make_filename]

    cmd = ['make'] + mfn + opts + args

    log.info("directory: {}".format(working_dir))
    log.info("command:")
    for i in cmd:
        log.info("    {}".format(i))

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
            "exception while starting make script\n" +
            "    command line was:\n" +
            "    " + repr(cmd) + "\n" +
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
                "exception occurred while waiting for builder\n" +
                wayround_org.utils.error.return_exception_info(
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

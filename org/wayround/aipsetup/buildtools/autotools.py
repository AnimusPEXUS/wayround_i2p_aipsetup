
"""
autotools tools and specific to it
"""

import os.path
import subprocess
import shutil
import sys
import tempfile

import org.wayround.aipsetup.buildingsite
import org.wayround.utils.osutils
import org.wayround.utils.archive
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


def extract_high(
    building_site,
    tarball_basename,
    unwrap_dir,
    rename_dir
    ):

    ret = 0

    building_site = os.path.abspath(building_site)

    log = org.wayround.utils.log.Log(
        org.wayround.aipsetup.buildingsite.getDIR_BUILD_LOGS(building_site),
        'extract'
        )

    building_site = os.path.abspath(building_site)

    tarball_dir = org.wayround.aipsetup.buildingsite.getDIR_TARBALL(building_site)

    source_dir = org.wayround.aipsetup.buildingsite.getDIR_SOURCE(building_site)

    tarball_dir_files = os.listdir(tarball_dir)

    tarball_dir_files_len = len(tarball_dir_files)

    tmpdir = tempfile.mkdtemp(
        dir=org.wayround.aipsetup.buildingsite.getDIR_TEMP(building_site)
        )

    if tarball_dir_files_len == 0:
        log.error("No Source Tarball Supplied")
        ret = 1
    else:

        tarball = None
        for i in tarball_dir_files:
            parsed = org.wayround.aipsetup.name.source_name_parse(
                i, mute=True
                )
            if isinstance(parsed, dict):
                if parsed['groups']['name'] == tarball_basename:
                    tarball = tarball_dir + os.path.sep + i
                    break

        if not tarball:
            log.error("Couldn't find acceptable tarball for current building site")
            ret = 2
        else:

            ret = extract_low(
                log,
                tmpdir,
                tarball,
                source_dir,
                unwrap_dir=unwrap_dir,
                rename_dir=rename_dir
                )

    log.close()

    return ret


def extract_low(
    log,
    tmpdir,
    tarball,
    outdir,
    unwrap_dir=False,
    rename_dir=False
    ):

    ret = 0

    if not os.path.isdir(outdir):
        os.makedirs(outdir)

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
                    n = outdir + os.path.sep + str(rename_dir)
                    log.info("moving extracted dir as `{}'".format(n))
                    shutil.move(extracted_dir, n)
                else:
                    log.info("moving extracted dir to `{}'".format(outdir))
                    shutil.move(extracted_dir, outdir)

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

    ret = 0

    building_site = os.path.abspath(building_site)

    log = org.wayround.utils.log.Log(
        org.wayround.aipsetup.buildingsite.getDIR_BUILD_LOGS(building_site),
        'configure'
        )

    pkg_info = org.wayround.aipsetup.buildingsite.read_package_info(
        building_site
        )

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

    while r'//' in script_name:
        script_name = script_name.replace(r'//', '/')

    while r'//' in working_dir:
        working_dir = working_dir.replace(r'//', '/')

    while r'//' in script_path:
        script_path = script_path.replace(r'//', '/')

    if relative_call:
        script_path = os.path.relpath(script_path, working_dir)

    cmd = []
    if not run_script_not_bash:
        cmd = ['bash'] + [script_path + os.path.sep + script_name] + opts + args
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

    building_site = os.path.abspath(building_site)

    log = org.wayround.utils.log.Log(
        org.wayround.aipsetup.buildingsite.getDIR_BUILD_LOGS(building_site),
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

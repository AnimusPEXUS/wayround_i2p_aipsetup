
import os.path
import subprocess
import sys

import wayround_org.utils.error
import wayround_org.utils.log
import wayround_org.utils.osutils
import wayround_org.utils.path
import wayround_org.utils.file


def waf(
        cwd,
        options,
        arguments,
        environment,
        environment_mode,
        log
        ):

    ret = 0

    cwd = wayround_org.utils.path.abspath(cwd)

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

    if 'PYTHON' in environment:
        python = environment['PYTHON']
    else:
        if 'PATH' in environment:
            PATH = environment['PATH']
        else:
            PATH = os.environ['PATH']

        PATH = PATH.split(':')

        python = wayround_org.utils.file.which('python2', PATH)

        del PATH

    cmd = [
        python,
        wayround_org.utils.path.join(cwd, 'waf')
        ] + options + arguments

    log.info("directory: {}".format(cwd))
    log.info("command: {}".format(cmd))
    log.info("command(joined): {}".format(' '.join(cmd)))

    p = None
    try:
        p = subprocess.Popen(
            args=cmd,
            cwd=cwd,
            stdout=log.stdout,
            stderr=log.stderr,
            env=env
            )
    except:
        log.error(
            "exception while starting waf script\n"
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

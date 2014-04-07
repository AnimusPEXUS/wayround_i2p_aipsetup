
import os.path
import subprocess
import sys

import org.wayround.utils.error
import org.wayround.utils.log
import org.wayround.utils.osutils
import org.wayround.utils.path


def waf(
    cwd,
    options,
    arguments,
    environment,
    environment_mode,
    log
    ):

    ret = 0

    cwd = org.wayround.utils.path.abspath(cwd)

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

    cmd = [
        'python3',
        os.path.join(cwd, 'waf')
        ] + options + arguments

    log.info("directory: {}".format(cwd))
    log.info("command: {}".format(cmd))
    log.info("command(joined): {}".format(' '.join(cmd)))

    p = None
    try:
        p = subprocess.Popen(
            args=cmd,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env
            )
    except:
        log.error(
            "exception while starting waf script\n"
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

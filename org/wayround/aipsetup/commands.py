
import collections

import org.wayround.aipsetup.commands_local_build
import org.wayround.aipsetup.commands_local_sys
import org.wayround.aipsetup.commands_pkg_client
import org.wayround.aipsetup.commands_pkg_server
import org.wayround.aipsetup.commands_src_client
import org.wayround.aipsetup.commands_src_server


def commands():
    ret = collections.OrderedDict([

    ('config', {
        'init': config_init,
        'print': config_print
        })
    ])

    ret.update(org.wayround.aipsetup.commands_local_sys.commands())
    ret.update(org.wayround.aipsetup.commands_local_build.commands())
    ret.update(org.wayround.aipsetup.commands_pkg_client.commands())
    ret.update(org.wayround.aipsetup.commands_pkg_server.commands())
    ret.update(org.wayround.aipsetup.commands_src_client.commands())
    ret.update(org.wayround.aipsetup.commands_src_server.commands())

    return ret


def config_init(command_name, opts, args, adds):

    import org.wayround.aipsetup.config
    #    config = adds['config']
    org.wayround.aipsetup.config.save_config(
        '/etc/aipsetup.conf',
        org.wayround.aipsetup.config.DEFAULT_CONFIG
        )

    return 0


def config_print(command_name, opts, args, adds):

    import io

    config = adds['config']

    b = io.StringIO()

    config.write(b)

    b.seek(0)

    s = b.read()

    b.close()

    print(s)

    return

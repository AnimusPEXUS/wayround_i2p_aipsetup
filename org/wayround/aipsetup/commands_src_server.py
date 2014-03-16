
import collections


def commands():
    return collections.OrderedDict([
        ('src_server', {
            'start': src_server_start,
            'reindex': src_server_reindex
            })

        ])


def src_server_start(command_name, opts, args, adds):

    import org.wayround.aipsetup.server_src

    return org.wayround.aipsetup.server_src.src_server_start(
        command_name, opts, args, adds
        )


def src_server_reindex(command_name, opts, args, adds):

    import org.wayround.aipsetup.server_src

    return org.wayround.aipsetup.server_src.src_server_reindex(
        command_name, opts, args, adds
        )

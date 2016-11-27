
import collections
import logging
import os.path


import wayround_i2p.utils.path


def commands():
    return collections.OrderedDict([
        ('src-server',
            collections.OrderedDict([
                ('start', src_server_start),
                ('index', src_repo_index)
            ]))
        ])


def src_server_start(command_name, opts, args, adds):

    import wayround_i2p.aipsetup.server_src

    return wayround_i2p.aipsetup.server_src.src_server_start(
        command_name, opts, args, adds
        )


def src_repo_index(command_name, opts, args, adds):
    """
    Create sources and repositories indexes

    [-f] [SUBDIR]


    SUBDIR - index only one of subdirectories

    -f - force reindexing files already in index
    -c - only index clean
    """

    import wayround_i2p.aipsetup.controllers

    config = adds['config']

    ret = 0

    forced_reindex = '-f' in opts
    clean_only = '-c' in opts

    subdir_name = wayround_i2p.utils.path.abspath(
        config['src_server']['tarball_repository_root']
        )

    if len(args) > 1:
        logging.error("Wrong argument count: can be only one")
        ret = 1
    else:

        if len(args) > 0:
            subdir_name = args[0]
            subdir_name = wayround_i2p.utils.path.abspath(subdir_name)

        if True:
            # else:

            src_ctl = \
                wayround_i2p.aipsetup.controllers.\
                src_repo_ctl_by_config(config)

            ret = src_ctl.index_sources(
                wayround_i2p.utils.path.abspath(subdir_name),
                acceptable_src_file_extensions=(
                    config['src_server']['acceptable_src_file_extensions'].split()
                    ),
                force_reindex=forced_reindex,
                clean_only=clean_only
                )

    return ret


import collections
import logging
import os.path

import org.wayround.aipsetup.controllers
import org.wayround.utils.path


def commands():
    return collections.OrderedDict([
        ('src-server',
            collections.OrderedDict([
                ('start', src_server_start),
                ('index', src_repo_index),
                ('load-paths', load_paths),
                ('save-paths', save_paths)
            ]))
        ])


def src_server_start(command_name, opts, args, adds):

    import org.wayround.aipsetup.server_src

    return org.wayround.aipsetup.server_src.src_server_start(
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

    config = adds['config']

    ret = 0

    forced_reindex = '-f' in opts
    clean_only = '-c' in opts

    subdir_name = org.wayround.utils.path.realpath(
        org.wayround.utils.path.abspath(
                config['src_server']['tarball_repository_root']
            )
        )

    if len(args) > 1:
        logging.error("Wrong argument count: can be only one")
        ret = 1
    else:

        if len(args) > 0:
            subdir_name = args[0]
            subdir_name = org.wayround.utils.path.realpath(
                org.wayround.utils.path.abspath(subdir_name)
                )

        if (
            not (
                org.wayround.utils.path.realpath(
                    org.wayround.utils.path.abspath(subdir_name)
                    ) + '/'
                 ).startswith(
                    org.wayround.utils.path.realpath(
                        org.wayround.utils.path.abspath(
                            config['src_server']['tarball_repository_root']
                            )
                        ) + '/'
                    )
            or not os.path.isdir(org.wayround.utils.path.abspath(subdir_name))
            ):
            logging.error("Not a subdir of pkg_source: {}".format(subdir_name))
            logging.debug(
"""\
passed: {}
config: {}
exists: {}
""".format(
                    org.wayround.utils.path.realpath(
                        org.wayround.utils.path.abspath(subdir_name)
                        ),
                    org.wayround.utils.path.realpath(
                        org.wayround.utils.path.abspath(
                            config['src_server']['tarball_repository_root']
                            )
                        ),
                    os.path.isdir(subdir_name)
                    )
                )
            ret = 2

        else:

            src_ctl = \
                org.wayround.aipsetup.controllers.\
                    src_repo_ctl_by_config(config)

            ret = src_ctl.index_sources(
                org.wayround.utils.path.realpath(subdir_name),
                acceptable_src_file_extensions=(
                    config['src_server']['acceptable_src_file_extensions']
                    ),
                force_reindex=forced_reindex,
                clean_only=clean_only
                )

    return ret


def save_paths(command_name, opts, args, adds):
    ret = 0

    config = adds['config']

    src_paths_repo_ctl = \
        org.wayround.aipsetup.controllers.src_paths_repo_ctl_by_config(config)

    src_paths_repo_ctl.save()

    return ret


def load_paths(command_name, opts, args, adds):
    ret = 0

    config = adds['config']

    src_paths_repo_ctl = \
        org.wayround.aipsetup.controllers.src_paths_repo_ctl_by_config(config)

    src_paths_repo_ctl.load()

    return ret

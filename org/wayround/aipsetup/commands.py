
import collections
import datetime
import functools
import logging
import os.path

import org.wayround.aipsetup.controllers
import org.wayround.aipsetup.commands_local_sys
import org.wayround.aipsetup.commands_local_build
import org.wayround.aipsetup.commands_pkg_server
import org.wayround.aipsetup.commands_src_server
import org.wayround.aipsetup.commands_pkg_client
import org.wayround.aipsetup.commands_src_client
import org.wayround.aipsetup.info
import org.wayround.aipsetup.package_name_parser
import org.wayround.aipsetup.sysupdates
import org.wayround.aipsetup.version
import org.wayround.utils.getopt
import org.wayround.utils.log
import org.wayround.utils.path
import org.wayround.utils.time


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

    config = adds['config']

    org.wayround.aipsetup.config.save_config(
        '/etc/aipsetup.conf',
        org.wayround.aipsetup.config.DEFAULT_CONFIG
        )

    return 0


def config_print(command_name, opts, args, adds):

    import org.wayround.aipsetup.config
    import io

    config = adds['config']

    b = io.StringIO()

    config.write(b)

    b.seek(0)

    s = b.read()

    b.close()

    print(s)

    return


# TODO: remove this function
def test_test(command_name, opts, args, adds):

    """
    Test documentation

    123
    """

    print("""\
config: {}

opts: {}

args: {}
""".format(command_name, opts, args, adds))

    return 0


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
                config['sources_repo']['dir']
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
                            config['sources_repo']['dir']
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
                            config['sources_repo']['dir']
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
                    config['general']['acceptable_src_file_extensions'].\
                        split()
                    ),
                force_reindex=forced_reindex,
                clean_only=clean_only
                )

    return ret


def src_repo_search_name(command_name, opts, args, adds):

    """
    Search for basenames in index using file name mask

    -r - Use RegExp instead of file name mask
    -s - be case sensitive
    """

    config = adds['config']

    ret = 0

    if org.wayround.utils.getopt.check_options(
            opts,
            opts_list=[
                '-r',
                '-s'
                ]
            ) != 0:
        ret = 1

    if ret == 0:

        mode = 'fm'
        mask = '*'
        case_sensetive = False

        if '-r' in opts:
            mode = 're'

        if '-s' in opts:
            case_sensetive = True

        if len(args) > 0:
            mask = args[0]

        logging.info("Loading")

        src_index = \
            org.wayround.aipsetup.controllers.src_repo_ctl_by_config(config)

        logging.info("Searching")

        names = src_index.find_name(mode, mask, cs=case_sensetive)

        names.sort()

        for i in names:
            print("    {}".format(i))

    return ret


def src_repo_print_paths(command_name, opts, args, adds):

    """
    Print paths of tarballs in source repository using package name

    -b - use tarball base name, not package name
    """

    config = adds['config']

    ret = 0

    if org.wayround.utils.getopt.check_options(
            opts,
            opts_list=[
                '-b'
                ]
            ) != 0:
        ret = 1

    if ret == 0:

        namemode = 'packagename'

        if '-b' in opts:
            namemode = 'basename'

        name = None

        if not len(args) == 1:
            ret = 1
            logging.error("One argument required")
        else:
            name = args[0]

            if namemode == 'packagename':
                info_ctl = \
                    org.wayround.aipsetup.controllers.\
                        info_ctl_by_config(config)
                info_rec = info_ctl.get_package_info_record(name)

            if namemode == 'packagename' and not info_rec:
                logging.error("Can't determine package's tarball basename")
                ret = 2
            else:

                if namemode == 'packagename':
                    basename = info_rec['basename']
                else:
                    basename = name

                src_index = \
                    org.wayround.aipsetup.controllers.\
                        src_repo_ctl_by_config(config)

                if namemode == 'basename':
                    objects = src_index.get_name_paths(basename)
                elif namemode == 'packagename':
                    objects = src_index.get_package_source_files(
                        basename,
                        info_ctl,
                        filtered=True
                        )

                if not isinstance(objects, list):
                    ret = 10
                else:
                    objects.sort(
                        key=functools.cmp_to_key(
                        org.wayround.utils.version.source_version_comparator
                            )
                        )
                    for i in objects:
                        st = os.stat(
                            org.wayround.utils.path.join(
                                src_index.sources_dir,
                                i
                                )
                            )
                        mtime = st.st_mtime

                        print(
                            '    {} ({})'.format(
                                i,
                                datetime.datetime.fromtimestamp(mtime)
                                )
                            )

    return ret


def src_repo_get_file(command_name, opts, args, adds):

    config = adds['config']

    ret = 0

    dstdir = '.'
    filename = None

    if org.wayround.utils.getopt.check_options(
            opts,
            opts_list=[
                '-o='
                ]
            ) != 0:
        ret = 1

    if ret == 0:

        if '-o' in opts:
            dstdir = opts['-o']

        if len(args) != 0:
            filename = args[0]

        if not filename:
            logging.error("File name required")
            ret = 1
        else:

            src_index = \
                org.wayround.aipsetup.controllers.\
                    src_repo_ctl_by_config(config)
            ret = src_index.get_file(filename, dstdir)

    return 0


def src_repo_get_latest_tarball(command_name, opts, args, adds):

    """
    Download latest tarball by given package names

    -o=OUTPUT_DIR - defaults to current
    """

    config = adds['config']

    ret = 0

    if org.wayround.utils.getopt.check_options(
            opts,
            opts_list=['-o=']
            ) != 0:
        ret = 1

    if ret == 0:

        names = None
        dstdir = '.'

        if '-o' in opts:
            dstdir = opts['-o']

        if len(args) != 0:
            names = args

        if len(names) == 0:
            logging.error("package name required")
            ret = 1

        if ret == 0:

            info_ctl = \
                org.wayround.aipsetup.controllers.info_ctl_by_config(config)

            src_index = \
                org.wayround.aipsetup.controllers.\
                    src_repo_ctl_by_config(config)

            logging.info("Loading index")
            for name in names:

                ret = src_index.get_latest_file(
                    package_name=name,
                    out_dir=dstdir,
                    info_ctl=info_ctl,
                    verbose=True,
                    mute=False
                    )

    return ret


def src_repo_get_latest_tarball_categorised(command_name, opts, args, adds):

    config = adds['config']

    ret = 0

    if org.wayround.utils.getopt.check_options(
            opts,
            opts_list=['-o=']
            ) != 0:
        ret = 1

    if ret == 0:

        category = None
        dstdir = '.'

        if '-o' in opts:
            dstdir = opts['-o']

        if len(args) != 0:
            category = args[0]

        if category == None:
            logging.error("category path required")
            ret = 1

        if ret == 0:

            logging.info("Loading indexes")
            info_ctl = \
                org.wayround.aipsetup.controllers.info_ctl_by_config(config)
            pkg_repo_ctl = \
                org.wayround.aipsetup.controllers.\
                    pkg_repo_ctl_by_config(config)
            src_repo_ctl = \
                org.wayround.aipsetup.controllers.\
                    src_repo_ctl_by_config(config)

            ret = src_repo_ctl.get_latest_files_by_category(
                category,
                out_dir=dstdir,
                pkg_repo_ctl=pkg_repo_ctl,
                info_ctl=info_ctl,
                verbose=True,
                mute=False
                )

    return ret


def src_repo_check_registartions(command_name, opts, args, adds):

    config = adds['config']

    ret = 0

    if org.wayround.utils.getopt.check_options(
            opts,
            opts_list=[]
            ) != 0:
        ret = 1

    if ret == 0:

        path = ''

        if len(args) != 0:
            path = args[0]

        info_ctl = org.wayround.aipsetup.controllers.info_ctl_by_config(config)
        src_repo_ctl = \
            org.wayround.aipsetup.controllers.src_repo_ctl_by_config(config)
        res = src_repo_ctl.check_tarball_basenames_registration(path, info_ctl)

        keys = list(res.keys())
        keys.sort()

        longest_name = 0
        for i in keys:

            l = len(i)

            if l > longest_name:
                longest_name = l

        longest_pkg_name = 0
        for i in keys:

            if res[i]:
                l = len(res[i]['name'])

                if l > longest_pkg_name:
                    longest_pkg_name = l

        for i in keys:
            if res[i]:
                print(
                    "    {name}: {pkg_name}, {deprecated}, {non_installable},"
                    " {removable}, {reducible}".format(
                        name=i.ljust(longest_name),
                        pkg_name=res[i]['name'].ljust(longest_pkg_name),
                        deprecated=str(res[i]['deprecated']).ljust(5),
                        non_installable=str(
                            res[i]['non_installable']
                            ).ljust(5),
                        removable=str(res[i]['removable']).ljust(5),
                        reducible=str(res[i]['reducible']).ljust(5)
                        )
                    )
            else:
                print(
                    "    {name}: NOT REGISTERED".format(
                        name=i.ljust(longest_name)
                        )
                    )

    return ret

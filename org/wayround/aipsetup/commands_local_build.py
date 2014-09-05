
import collections
import logging
import os.path

import org.wayround.aipsetup.build
import org.wayround.aipsetup.controllers


def commands():
    return collections.OrderedDict([
        ('bsite', collections.OrderedDict([
            ('init', building_site_init),
            ('apply', building_site_apply_info)
            ])),
        ('build', collections.OrderedDict([
            ('full', build_full),
            ('build', build_build),
            ('continue', build_build_plus),
            ('pack', build_pack),
            ('complete', build_complete),
            ]))
        ])


def building_site_init(command_name, opts, args, adds):
    """
    Initiate new building site dir, copying spplyed tarballs to 00.TARBALLS

    [DIRNAME] [TARBALL [TARBALL [TARBALL ...]]]
    """

    #    config = adds['config']

    init_dir = '.'

    if len(args) > 0:
        init_dir = args[0]

    files = None
    if len(args) > 1:
        files = args[1:]

    bs = org.wayround.aipsetup.controllers.bsite_ctl_new(init_dir)

    ret = bs.init(files)

    return ret


def building_site_apply_info(command_name, opts, args, adds):
    """
    Apply info to building dir

    [DIRNAME [FILENAME]]
    """

    config = adds['config']

    dirname = '.'
    file = None

    if len(args) > 0:
        dirname = args[0]

    if len(args) > 1:
        file = args[1]

    # TODO: add check for dirname correctness

    host = config['system_settings']['host']
    build = config['system_settings']['build']
    target = config['system_settings']['target']

    if '--host' in opts:
        host = opts['--host']

    if '--build' in opts:
        build = opts['--build']

    if '--target' in opts:
        target = opts['--target']

    const = org.wayround.aipsetup.controllers.constitution_by_config(
        config,
        host,
        target,
        build
        )

    bs = org.wayround.aipsetup.controllers.bsite_ctl_new(dirname)
    pkg_client = org.wayround.aipsetup.controllers.pkg_client_by_config(config)
    ret = bs.apply_info(pkg_client, const, src_file_name=file)

    return ret


def build_build_plus(command_name, opts, args, adds):
    """
    Starts named action from script applied to current building site

    [-b=DIR] action_name

    -b - set building site

    if action name ends with + (plus) all remaining actions will be also
    started (if not error will occur)
    """

    config = adds['config']

    ret = 0

    args_l = len(args)

    if args_l != 1:
        logging.error("one argument must be")
        ret = 1
    else:

        action = args[0]

        dirname = '.'
        if '-b' in opts:
            dirname = opts['-b']

        bs = org.wayround.aipsetup.controllers.bsite_ctl_new(dirname)
        build_ctl = org.wayround.aipsetup.controllers.build_ctl_new(bs)
        script = \
            org.wayround.aipsetup.controllers.bscript_ctl_by_config(config)
        ret = build_ctl.start_building_script(script, action=action)

    return ret


def _build_complete_subroutine(
        config,
        host,
        target,
        build,
        dirname,
        file,
        r_bds
        ):

    ret = 0

    const = org.wayround.aipsetup.controllers.constitution_by_config(
        config,
        host,
        target,
        build
        )

    if const == None:
        ret = 1
    else:

        bs = org.wayround.aipsetup.controllers.bsite_ctl_new(dirname)

        build_ctl = org.wayround.aipsetup.controllers.build_ctl_new(bs)
        pack_ctl = org.wayround.aipsetup.controllers.pack_ctl_new(bs)

        build_script_ctl = \
            org.wayround.aipsetup.controllers.bscript_ctl_by_config(config)

        pkg_client = \
            org.wayround.aipsetup.controllers.pkg_client_by_config(config)

        ret = bs.complete(
            build_ctl,
            pack_ctl,
            build_script_ctl,
            pkg_client,
            main_src_file=file,
            remove_buildingsite_after_success=r_bds,
            const=const
            )

    return ret


def build_complete(command_name, opts, args, adds):
    """
    Complete package building process in existing building site

    [DIRNAME] [TARBALL]

    [DIRNAME1] [DIRNAME2] [DIRNAMEn]

    This command has two modes of work:

       1. Working with single dir, which is pointed or not pointed by
          first parameter. In this mode, a tarball can be passed,
          which name will be used to apply new package info to pointed
          dir. By default DIRNAME is \`.\' (current dir)

       2. Working with multiple dirs. In this mode, tarball can't be
          passed.

    options:

    ================ ====================================
    options          meaning
    ================ ====================================
    -d               remove building site on success
    --host=TRIPLET
    --build=TRIPLET
    --target=TRIPLET
    ================ ====================================
    """

    config = adds['config']

    ret = 0

    r_bds = '-d' in opts

    host = config['system_settings']['host']
    build = config['system_settings']['build']
    target = config['system_settings']['target']

    if '--host' in opts:
        host = opts['--host']

    if '--build' in opts:
        build = opts['--build']

    if '--target' in opts:
        target = opts['--target']

    args_l = len(args)

    if args_l == 0:

        ret = _build_complete_subroutine(
            config,
            host,
            target,
            build,
            '.',
            None,
            r_bds
            )

    elif args_l == 1 and os.path.isfile(args[0]):

        ret = _build_complete_subroutine(
            config,
            host,
            target,
            build,
            '.',
            args[0],
            r_bds
            )

    elif args_l == 2 and os.path.isdir(args[0]) and os.path.isfile(args[1]):

        ret = _build_complete_subroutine(
            config,
            host,
            target,
            build,
            args[0],
            args[1],
            r_bds
            )

    else:

        error = False

        for i in args:

            if _build_complete_subroutine(
                    config,
                    host,
                    target,
                    build,
                    i,
                    None,
                    r_bds
                    ) != 0:
                error = True

        ret = int(error)

    return ret


def build_full(command_name, opts, args, adds):
    """
    Place named source files in new building site and build new package from
    them

    [-d] [-o] [--host=HOST-NAME-TRIPLET] TARBALL[, TARBALL[, TARBALL[,
                                                                TARBALL...]]]

    ================ ====================================
    options          meaning
    ================ ====================================
    -d               remove building site on success
    -o               treat all tarballs as for one build
    --host=TRIPLET
    --build=TRIPLET
    --target=TRIPLET
    ================ ====================================
    """

    config = adds['config']

    r_bds = '-d' in opts

    sources = []

    multiple_packages = not '-o' in opts

    ret = 0

    building_site_dir = config['local_build']['building_scripts_dir']

    host = config['system_settings']['host']
    build = config['system_settings']['build']
    target = config['system_settings']['target']

    if len(args) > 0:
        sources = args
        building_site_dir = org.wayround.utils.path.abspath(
            os.path.dirname(sources[0])
            )

    if len(sources) == 0:
        logging.error("No source files supplied")
        ret = 2

    if '--host' in opts:
        host = opts['--host']

    if '--build' in opts:
        build = opts['--build']

    if '--target' in opts:
        target = opts['--target']

    if ret == 0:

        logging.info("Applying constitution")
        const = org.wayround.aipsetup.controllers.constitution_by_config(
            config,
            host,
            target,
            build
            )

        if not isinstance(const, org.wayround.aipsetup.build.Constitution):
            ret = 1
        else:

            if multiple_packages:
                sources.sort()
                rets = 0
                logging.info("Passing packages `{}' to build".format(sources))
                for i in sources:
                    if org.wayround.aipsetup.build.build(
                            config,
                            [i],
                            remove_buildingsite_after_success=r_bds,
                            buildingsites_dir=building_site_dir,
                            const=const
                            ) != 0:
                        rets += 1
                if rets == 0:
                    ret = 0
                else:
                    ret = 1
            else:
                logging.info("Passing package `{}' to build".format(sources))
                ret = org.wayround.aipsetup.build.build(
                    config,
                    sources,
                    remove_buildingsite_after_success=r_bds,
                    buildingsites_dir=building_site_dir,
                    const=const
                    )

    return ret


def build_pack(command_name, opts, args, adds):
    """
    Fullcircle action set for creating package

    [DIRNAME]

    DIRNAME - set building site. Default is current directory
    """

    ret = 0

    dir_name = '.'
    args_l = len(args)

    if args_l > 1:
        logging.error("Too many parameters")

    else:
        if args_l == 1:
            dir_name = args[0]

        bs = org.wayround.aipsetup.controllers.bsite_ctl_new(dir_name)

        packer = org.wayround.aipsetup.controllers.pack_ctl_new(bs)

        ret = packer.complete()

    return ret


def build_build(command_name, opts, args, adds):
    """
    Configures, builds, distributes and prepares software accordingly to info

    [DIRNAME]

    DIRNAME - set building site. Default is current directory
    """

    config = adds['config']

    ret = 0

    dir_name = '.'
    args_l = len(args)

    if args_l > 1:
        logging.error("Too many parameters")

    else:
        if args_l == 1:
            dir_name = args[0]

        bs = org.wayround.aipsetup.controllers.bsite_ctl_new(dir_name)

        build_ctl = org.wayround.aipsetup.controllers.build_ctl_new(bs)

        buildscript_ctl = \
            org.wayround.aipsetup.controllers.bscript_ctl_by_config(config)

        ret = build_ctl.complete(buildscript_ctl)

    return ret

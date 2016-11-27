
import collections
import logging
import os.path
import tempfile


import wayround_org.utils.path


def commands():
    return collections.OrderedDict([
        ('build', collections.OrderedDict([
            ('full', build_full),
            ('full_ho', build_full_hosts),
            ('full_ar', build_full_archs),
            ('build', build_build),
            ('continue', build_continue),
            ('pack', build_pack),
            ('complete', build_complete),
            ('site', collections.OrderedDict([
                ('init', building_site_init),
                ('apply', building_site_apply_info),
                ('apply-by-name', building_site_apply_info_by_name)
                ]))
            ]))
        ])


def building_site_init(command_name, opts, args, adds):
    """
    Initiate new building site dir, copying spplyed tarballs to 00.TARBALLS

    [DIRNAME] [TARBALL [TARBALL [TARBALL ...]]]
    """

    import wayround_org.aipsetup.controllers

    #    config = adds['config']

    init_dir = '.'

    if len(args) > 0:
        init_dir = args[0]

    files = None
    if len(args) > 1:
        files = args[1:]

    bs = wayround_org.aipsetup.controllers.bsite_ctl_new(init_dir)

    ret = bs.init(files)

    return ret


def building_site_apply_info(command_name, opts, args, adds):
    """
    Apply info to building dir

    [DIRNAME [FILENAME]]
    """

    import wayround_org.aipsetup.controllers

    config = adds['config']

    dirname = '.'
    file = None

    if len(args) > 0:
        dirname = args[0]

    if len(args) > 1:
        file = args[1]

    # TODO: add check for dirname correctness

    pkg_info = wayround_org.aipsetup.build.read_package_info(
        dirname,
        None
        )

    host, build, target, arch, ccp_res = \
        wayround_org.aipsetup.build.constitution_configurer(
            config,
            pkg_info,
            opts.get('--host', None),
            opts.get('--build', None),
            opts.get('--target', None),
            opts.get('--arch', None)
            )

    const = wayround_org.aipsetup.build.Constitution(
        host,
        build,
        target,
        arch,
        ccp_res['multilib_variants'],
        ccp_res['CC'],
        ccp_res['CXX']

        )

    bs = wayround_org.aipsetup.controllers.bsite_ctl_new(dirname)
    pkg_client = wayround_org.aipsetup.controllers.pkg_client_by_config(config)
    ret = bs.apply_info(pkg_client, const, src_file_name=file)

    return ret


def building_site_apply_info_by_name(command_name, opts, args, adds):
    """
    Apply info to building dir

    [DIRNAME] PACKAGE_INFO_NAME
    """

    import wayround_org.aipsetup.controllers

    config = adds['config']

    dirname = '.'
    package_name = None

    len_args = len(args)

    if len_args == 1:
        dirname = '.'
        package_name = args[0]

    elif len_args == 2:
        dirname = args[0]
        package_name = args[1]

    else:
        logging.error("Must be 1 or 2 parameters")
        ret = 1

    pkg_info = wayround_org.aipsetup.build.read_package_info(
        dirname,
        None
        )

    host, build, target, arch, ccp_res = \
        wayround_org.aipsetup.build.constitution_configurer(
            config,
            pkg_info,
            opts.get('--host', None),
            opts.get('--build', None),
            opts.get('--target', None),
            opts.get('--arch', None)
            )

    const = wayround_org.aipsetup.build.Constitution(
        host,
        build,
        target,
        paths,
        arch,
        ccp_res['multilib_variants'],
        ccp_res['CC'],
        ccp_res['CXX']
        )

    bs = wayround_org.aipsetup.controllers.bsite_ctl_new(dirname)
    pkg_client = wayround_org.aipsetup.controllers.pkg_client_by_config(config)
    ret = bs.apply_info_by_name(pkg_client, const, package_name)

    return ret


def build_continue(command_name, opts, args, adds):
    """
    Starts named action from script applied to current building site

    [-b=DIR] action_name

    -b - set building site

    if action name ends with + (plus) all remaining actions will be also
    started (if not error will occur)
    """

    import wayround_org.aipsetup.controllers

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

        bs = wayround_org.aipsetup.controllers.bsite_ctl_new(dirname)
        build_ctl = wayround_org.aipsetup.controllers.build_ctl_new(bs)
        script = \
            wayround_org.aipsetup.controllers.bscript_ctl_by_config(config)
        ret = build_ctl.start_building_script(script, action=action)

    return ret


def _build_complete_subroutine(
        config,
        host,
        build,
        target,
        arch,
        ccp_res,
        dirname,
        main_src_file,
        remove_buildingsite_after_success
        ):

    import wayround_org.aipsetup.controllers

    ret = 0

    print("host: {}".format(host))
    print("build: {}".format(build))
    print("target: {}".format(target))
    print("arch: {}".format(arch))

    const = wayround_org.aipsetup.build.Constitution(
        host,
        build,
        target,
        arch,
        ccp_res['multilib_variants'],
        ccp_res['CC'],
        ccp_res['CXX']
        )

    if const is None:
        ret = 1
    else:

        bs = wayround_org.aipsetup.controllers.bsite_ctl_new(dirname)

        build_ctl = wayround_org.aipsetup.controllers.build_ctl_new(bs)
        pack_ctl = wayround_org.aipsetup.controllers.pack_ctl_new(bs)

        build_script_ctl = \
            wayround_org.aipsetup.controllers.bscript_ctl_by_config(config)

        pkg_client = \
            wayround_org.aipsetup.controllers.pkg_client_by_config(config)

        ret = bs.complete(
            build_ctl,
            pack_ctl,
            build_script_ctl,
            pkg_client,
            main_src_file=main_src_file,
            remove_buildingsite_after_success=remove_buildingsite_after_success,
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

    import wayround_org.aipsetup.controllers

    config = adds['config']

    ret = 0

    r_bds = '-d' in opts

    args_l = len(args)

    if args_l == 0:

        pkg_info = wayround_org.aipsetup.build.read_package_info(
            '.',
            None
            )

        host, build, target, arch, ccp_res = \
            wayround_org.aipsetup.build.constitution_configurer(
                config,
                pkg_info,
                opts.get('--host', None),
                opts.get('--build', None),
                opts.get('--target', None),
                opts.get('--arch', None)
                )

        ret = _build_complete_subroutine(
            config,
            host,
            build,
            target,
            arch,
            ccp_res,
            '.',
            None,
            r_bds
            )

    elif args_l == 1 and os.path.isfile(args[0]):

        pkg_info = wayround_org.aipsetup.build.read_package_info(
            '.',
            None
            )

        host, build, target, arch, ccp_res = \
            wayround_org.aipsetup.build.constitution_configurer(
                config,
                pkg_info,
                opts.get('--host', None),
                opts.get('--build', None),
                opts.get('--target', None),
                opts.get('--arch', None)
                )

        ret = _build_complete_subroutine(
            config,
            host,
            build,
            target,
            arch,
            ccp_res,
            '.',
            args[0],
            r_bds
            )

    elif args_l == 2 and os.path.isdir(args[0]) and os.path.isfile(args[1]):

        pkg_info = wayround_org.aipsetup.build.read_package_info(
            args[0],
            None
            )

        host, build, target, arch, ccp_res = \
            wayround_org.aipsetup.build.constitution_configurer(
                config,
                pkg_info,
                opts.get('--host', None),
                opts.get('--build', None),
                opts.get('--target', None),
                opts.get('--arch', None)
                )

        ret = _build_complete_subroutine(
            config,
            host,
            build,
            target,
            arch,
            ccp_res,
            args[0],
            args[1],
            r_bds
            )

    else:

        error = False

        for i in args:

            pkg_info = wayround_org.aipsetup.build.read_package_info(
                i,
                None
                )

            host, build, target, arch, ccp_res = \
                wayround_org.aipsetup.build.constitution_configurer(
                    config,
                    pkg_info,
                    opts.get('--host', None),
                    opts.get('--build', None),
                    opts.get('--target', None),
                    opts.get('--arch', None)
                    )

            if _build_complete_subroutine(
                    config,
                    host,
                    build,
                    target,
                arch,
                ccp_res,
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

    [-d] [-o]
    [--host=VALUE] [--build=VALUE] [--target=VALUE] [--arch=VALUE]
    TARBALL1 .. TARBALLn

    ================ ====================================
    options          meaning
    ================ ====================================
    -d               remove building site on success
    -o               treat all tarballs as for one build
    --host=VALUE
    --build=VALUE
    --target=VALUE
    --arch=VALUE
    ================ ====================================
    """

    import wayround_org.aipsetup.build
    import wayround_org.aipsetup.controllers

    ret = 0

    config = adds['config']

    if wayround_org.utils.getopt.check_options(
            opts,
            opts_list=[
                '-d',
                '-o',
                '--host=',
                '--build=',
                '--target=',
                '--arch='
                ]
            ) != 0:
        raise Exception("Invalid Parameters")

    r_bds = '-d' in opts

    sources = []

    multiple_packages = not '-o' in opts

    if ret == 0:

        building_site_dir = config['local_build']['building_sites_dir']

        if len(args) > 0:
            sources = args
            building_site_dir = wayround_org.utils.path.abspath(
                os.path.dirname(sources[0])
                )

        if len(sources) == 0:
            logging.error("No source files supplied")
            ret = 2

        archs_list = [config['system_settings']['host']]

    if ret == 0:

        if multiple_packages:
            sources.sort()
            rets = 0
            logging.info("Passing packages `{}' to build".format(sources))
            for i in sources:

                if build_sub_01(
                        command_name, opts, args, adds,
                        config,
                        [i],
                        building_site_dir,
                        remove_buildingsite_after_success=r_bds
                        ) != 0:
                    rets += 1

            ret = int(rets != 0)

        else:
            logging.info("Passing package `{}' to build".format(sources))
            ret = build_sub_01(
                command_name, opts, args, adds,
                config,
                sources,
                building_site_dir,
                remove_buildingsite_after_success=r_bds
                )

    return ret


def build_full_hosts(command_name, opts, args, adds):
    """
    Build for multiple hosts

    [-d] [-o] TARBALL1 .. TARBALLn

    ================ ======================================
    options          meaning
    ================ ======================================
    -d               remove building site on success
    -o               treat all tarballs as for single build
    ================ ======================================
    """

    import wayround_org.aipsetup.build
    import wayround_org.aipsetup.controllers

    ret = 0

    config = adds['config']

    if wayround_org.utils.getopt.check_options(
            opts,
            opts_list=[
                '-d',
                '-o'
                ]
            ) != 0:
        raise Exception("Invalid Parameters")

    r_bds = '-d' in opts

    sources = []

    multiple_packages = not '-o' in opts
    multiarch_build = True

    if ret == 0:

        building_site_dir = config['local_build']['building_sites_dir']

        if len(args) > 0:
            sources = args
            building_site_dir = wayround_org.utils.path.abspath(
                os.path.dirname(sources[0])
                )

        if len(sources) == 0:
            logging.error("No source files supplied")
            ret = 2

        archs_list = config['local_build']['multiple_arch_build'].split()

    if ret == 0:

        if multiple_packages:
            sources.sort()
            rets = 0
            logging.info("Passing packages `{}' to build".format(sources))
            for i in sources:

                for arch in archs_list:

                    opts.update({
                        '--host': arch,
                        '--target': arch,
                        '--build': arch,
                        '--arch': arch
                        })

                    if build_sub_01(
                            command_name, opts, args, adds,
                            config,
                            [i],
                            building_site_dir,
                            remove_buildingsite_after_success=r_bds
                            ) != 0:
                        rets += 1

            ret = int(rets != 0)

        else:
            logging.info("Passing package `{}' to build".format(sources))
            rets = 0

            for arch in archs_list:

                opts.update({
                    '--host': arch,
                    '--target': arch,
                    '--build': arch,
                    '--arch': arch
                    })

                if build_sub_01(
                        command_name, opts, args, adds,
                        config,
                        sources,
                        building_site_dir,
                        remove_buildingsite_after_success=r_bds
                        ) != 0:
                    rets += 1

            ret = int(rets != 0)

    return ret


def build_full_archs(command_name, opts, args, adds):
    """
    Build for multiple archs

    [-d] [-o] TARBALL1 .. TARBALLn

    ================ ====================================
    options          meaning
    ================ ====================================
    -d               remove building site on success
    -o               treat all tarballs as for one build
    ================ ====================================
    """

    import wayround_org.aipsetup.build
    import wayround_org.aipsetup.controllers

    ret = 0

    config = adds['config']

    if wayround_org.utils.getopt.check_options(
            opts,
            opts_list=[
                '-d',
                '-o'
                ]
            ) != 0:
        raise Exception("Invalid Parameters")

    r_bds = '-d' in opts

    sources = []

    multiple_packages = not '-o' in opts
    multiarch_build = True

    host = config['system_settings']['host']

    if ret == 0:

        building_site_dir = config['local_build']['building_sites_dir']

        if len(args) > 0:
            sources = args
            building_site_dir = wayround_org.utils.path.abspath(
                os.path.dirname(sources[0])
                )

        if len(sources) == 0:
            logging.error("No source files supplied")
            ret = 2

        archs_list = config['local_build']['multiple_arch_build'].split()

    if ret == 0:

        if multiple_packages:
            sources.sort()
            rets = 0
            logging.info("Passing packages `{}' to build".format(sources))
            for i in sources:

                for arch in archs_list:

                    opts.update({
                        '--host': host,
                        '--target': host,
                        '--build': host,
                        '--arch': arch
                        })

                    if build_sub_01(
                            command_name, opts, args, adds,
                            config,
                            [i],
                            building_site_dir,
                            remove_buildingsite_after_success=r_bds
                            ) != 0:
                        rets += 1

            ret = int(rets != 0)

        else:
            logging.info("Passing package `{}' to build".format(sources))
            rets = 0

            for arch in archs_list:

                opts.update({
                    '--host': host,
                    '--target': host,
                    '--build': host,
                    '--arch': arch
                    })

                if build_sub_01(
                        command_name, opts, args, adds,
                        config,
                        sources,
                        building_site_dir,
                        remove_buildingsite_after_success=r_bds
                        ) != 0:
                    rets += 1

            ret = int(rets != 0)

    return ret


def build_pack(command_name, opts, args, adds):
    """
    Fullcircle action set for creating package

    [DIRNAME]

    DIRNAME - set building site. Default is current directory
    """

    import wayround_org.aipsetup.controllers

    ret = 0

    dir_name = '.'
    args_l = len(args)

    if args_l > 1:
        logging.error("Too many parameters")

    else:
        if args_l == 1:
            dir_name = args[0]

        bs = wayround_org.aipsetup.controllers.bsite_ctl_new(dir_name)

        packer = wayround_org.aipsetup.controllers.pack_ctl_new(bs)

        ret = packer.complete()

    return ret


def build_build(command_name, opts, args, adds):
    """
    Configures, builds, distributes and prepares software accordingly to info

    [DIRNAME]

    DIRNAME - set building site. Default is current directory
    """

    import wayround_org.aipsetup.controllers

    config = adds['config']

    ret = 0

    dir_name = '.'
    args_l = len(args)

    if args_l > 1:
        logging.error("Too many parameters")

    else:
        if args_l == 1:
            dir_name = args[0]

        bs = wayround_org.aipsetup.controllers.bsite_ctl_new(dir_name)

        build_ctl = wayround_org.aipsetup.controllers.build_ctl_new(bs)

        buildscript_ctl = \
            wayround_org.aipsetup.controllers.bscript_ctl_by_config(config)

        ret = build_ctl.complete(buildscript_ctl)

    return ret


def build_sub_01(
        command_name, opts, args, adds,
        config,
        source_files,
        buildingsites_dir,
        remove_buildingsite_after_success=False,
        ):
    """
    Gathering function for all package building process

    Uses :func:`wayround_org.aipsetup.buildingsite.init` to create building
    site. Farther process controlled by :func:`complete`.

    :param source_files: tarball name or list of them.
    """

    ret = 0

    par_res = wayround_org.utils.tarball.parse_tarball_name(
        source_files[0],
        mute=True
        )

    if not isinstance(par_res, dict):
        logging.error("Can't parse source file name")
        ret = 1
    else:

        if not os.path.isdir(buildingsites_dir):
            try:
                os.makedirs(buildingsites_dir)
            except:
                logging.error(
                    "Can't create directory: {}".format(buildingsites_dir)
                    )

        if not os.path.isdir(buildingsites_dir):
            logging.error("Directory not exists: {}".format(buildingsites_dir))
            ret = 7

        else:

            pkg_client = \
                wayround_org.aipsetup.controllers.pkg_client_by_config(config)

            pkg_name = pkg_client.name_by_name(source_files[0])

            if pkg_name is None:
                logging.error(
                    "Can't determine package name."
                    " Is server running?".format(
                        source_files[0],
                        pkg_name
                        )
                    )
                ret = 10

            if ret == 0:
                if len(pkg_name) != 1:
                    logging.error("""\
Can't select between those package names (for {})
(please, fix package names to not make collisions):
   {}
""".format(
                        source_files[0],
                        pkg_name
                        )
                        )
                    ret = 4
                else:
                    pkg_name = pkg_name[0]

            if ret == 0:

                package_info = pkg_client.info(pkg_name)

                if not package_info:
                    logging.error(
                        "Can't get package "
                        "information for tarball `{}'".format(
                            source_files[0]
                            )
                        )
                    ret = 2
                else:

                    # tmp_dir_prefix = \
                    #     "{name}-{version}-{status}-{timestamp}-".format_map(
                    #         {
                    #             'name': package_info['name'],
                    #             'version': par_res['groups']['version'],
                    #             'status': par_res['groups']['status'],
                    #             'timestamp':
                    #                 wayround_org.utils.time.currenttime_stamp()
                    #             }
                    #         )

                    _ts = wayround_org.utils.time.currenttime_stamp()
                    while '.' in _ts:
                        _ts = _ts.replace('.', '')

                    tmp_dir_prefix = "{}-{}-{}-".format(
                        package_info['name'],
                        par_res['groups']['version'],
                        _ts
                        )

                    if '--host' in opts:
                        tmp_dir_prefix += '{}-'.format(opts['--host'])

                    build_site_dir = tempfile.mkdtemp(
                        prefix=tmp_dir_prefix,
                        dir=buildingsites_dir
                        )

                    bs = wayround_org.aipsetup.controllers.bsite_ctl_new(
                        build_site_dir
                        )

                    if bs.init(source_files) != 0:
                        logging.error("Error initiating temporary dir")
                        ret = 3
                    else:

                        pkg_info = wayround_org.aipsetup.build.read_package_info(
                            build_site_dir,
                            None
                            )

                        host, build, target, arch, ccp_res = \
                            wayround_org.aipsetup.build.constitution_configurer(
                                config,
                                pkg_info,
                                opts.get('--host', None),
                                opts.get('--build', None),
                                opts.get('--target', None),
                                opts.get('--arch', None)
                                )

                        ret = _build_complete_subroutine(
                            config,
                            host,
                            build,
                            target,
                            arch,
                            ccp_res,
                            build_site_dir,
                            source_files[0],
                            remove_buildingsite_after_success
                            )

                        if ret != 0:

                            logging.error("Package building failed")
                            ret = 5

                        else:
                            logging.info(
                                "Complete package building ended with no error"
                                )
                            ret = 0

    return ret

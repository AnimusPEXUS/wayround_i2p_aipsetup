
"""
Build software before packaging

This module provides functions for building package using building script (see
:mod:`buildscript<org.wayround.aipsetup.buildscript>` module for more info on
building scripts)
"""

import logging
import copy

import org.wayround.aipsetup.buildingsite
import org.wayround.aipsetup.buildscript

import org.wayround.utils.path



def build_script(opts, args):
    """
    Starts named action from script applied to current building site

    [-b=DIR] action_name
    
    -b - set building site
    
    if action name ends with + (plus) all remaining actions will be also started
    (if not error will occur)
    """

    ret = 0

    args_l = len(args)

    if args_l != 1:
        logging.error("one argument must be")
        ret = 1
    else:

        action = args[0]

        bs = '.'
        if '-b' in opts:
            bs = opts['-b']

        ret = start_building_script(bs, action)

    return ret



def build_complete(opts, args):
    """
    Configures, builds, distributes and prepares software accordingly to info

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

        ret = complete(dir_name)

    return ret



def complete(building_site):
    """
    Run all building script commands on selected building site

    See :func:`start_building_script`
    """
    return start_building_script(building_site, action=None)


def start_building_script(building_site, action=None):
    """
    Run selected action on building site using particular building script.

    :param building_site: path to building site directory

    :param action: can be None or concrete name of action in building script.
        if action name ends with + (plus) all remaining actions will be also
        started (if not error will occur)

    :rtype: 0 - if no error occurred
    """


    building_site = org.wayround.utils.path.abspath(building_site)

    package_info = org.wayround.aipsetup.buildingsite.read_package_info(
        building_site, ret_on_error=None
        )

    ret = 0

    if package_info == None:
        logging.error(
            "Error getting information "
            "from building site's(`{}') `package_info.json'".format(building_site)
            )
        ret = 1
    else:

        script = (
            org.wayround.aipsetup.buildscript.load_buildscript(
                package_info['pkg_info']['buildscript']
                )
            )

        if not isinstance(script, dict):
            logging.error("Some error while loading script")
            ret = 2
        else:

            try:
                ret = script['main'](building_site, action)
            except KeyboardInterrupt:
                raise
            except:
                logging.exception(
                    "Error starting `main' function in `{}'".format(
                        package_info['pkg_info']['buildscript']
                        )
                    )
                ret = 3
                
            logging.info("action `{}' ended with code {}".format(action, ret));

    return ret


def build(source_files, remove_buildingsite_after_success=False):
    """
    Gathering function for all package building process

    Uses :func:`org.wayround.aipsetup.buildingsite.init` to create building site.
    Farther process controlled by :func:`complete`.

    :param source_files: tarball name or list of them.
    """
    ret = 0

    par_res = org.wayround.aipsetup.name.source_name_parse(
        source_files[0],
        mute=True
        )


    if not isinstance(par_res, dict):
        logging.error("Can't parse source file name")
        ret = 1
    else:

        try:
            os.makedirs(org.wayround.aipsetup.config.config['buildingsites'])
        except:
            pass

        package_info = (
            org.wayround.aipsetup.pkginfo.get_info_rec_by_tarball_filename(
                source_files[0]
                )
            )

        if not package_info:
            logging.error(
                "Can't find package information for tarball `{}'".format(
                    source_files[0]
                    )
                )
            ret = 2
        else:

            tmp_dir_prefix = "{name}-{version}-{status}-{timestamp}-".format_map(
                {
                    'name': package_info['name'],
                    'version': par_res['groups']['version'],
                    'status': par_res['groups']['status'],
                    'timestamp': org.wayround.utils.time.currenttime_stamp()
                    }
                )

            build_site_dir = tempfile.mkdtemp(
                prefix=tmp_dir_prefix,
                dir=org.wayround.aipsetup.config.config['buildingsites']
                )

            build_site_dir = org.wayround.utils.path.abspath(build_site_dir)

            if org.wayround.aipsetup.buildingsite.init(build_site_dir) != 0:
                logging.error("Error initiating temporary dir")
                ret = 3
            else:
                if source_files != None and isinstance(source_files, list):

                    logging.info("Copying sources...")

                    for source_file in source_files:

                        logging.info("    {}".format(source_file))

                        if (os.path.isfile(source_file)
                            and not os.path.islink(source_file)):

                            try:
                                shutil.copy(
                                    source_file, os.path.join(
                                        build_site_dir,
                                        org.wayround.aipsetup.buildingsite.DIR_TARBALL
                                        )
                                    )
                            except:
                                logging.exception("Couldn't copy source file")
                                ret = 4

                        else:

                            logging.error(
                                "file {} - not dir and not file. skipping copy".format(
                                    source_file
                                    )
                                )

                    if ret != 0:
                        logging.error(
                            "Exception while copying one of source files"
                            )

                if ret == 0:

                    # FIXME: rework this
                    if complete(
                        build_site_dir,
                        source_files[0],
                        remove_buildingsite_after_success=remove_buildingsite_after_success
                        ) != 0:

                        logging.error("Package building failed")
                        ret = 5

    return ret

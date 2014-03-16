
import logging

import org.wayround.aipsetup.build
import org.wayround.aipsetup.dbconnections
import org.wayround.aipsetup.info
import org.wayround.aipsetup.package
import org.wayround.aipsetup.repository
import org.wayround.aipsetup.system
import org.wayround.utils.system_type


def pkg_repo_ctl_by_config(config):

    db_connection = org.wayround.aipsetup.dbconnections.pkg_repo_db(config)

    repository_dir = config['package_repo']['dir']
    garbage_dir = config['package_repo']['garbage_dir']

    ret = pkg_repo_ctl_new(repository_dir, db_connection, garbage_dir)

    return ret


def pkg_repo_ctl_new(repository_dir, garbage_dir, pkg_repo_db):

    ret = org.wayround.aipsetup.repository.PackageRepoCtl(
        repository_dir, pkg_repo_db, garbage_dir
        )

    return ret


def src_repo_ctl_by_config(config):

    database_connection = \
        org.wayround.aipsetup.dbconnections.src_repo_db(config)

    sources_dir = config['sources_repo']['dir']
    ret = src_repo_ctl_new(sources_dir, database_connection)

    return ret


def src_repo_ctl_new(sources_dir, src_repo_db):

    ret = org.wayround.aipsetup.repository.SourceRepoCtl(
        sources_dir, src_repo_db
        )

    return ret


def info_ctl_by_config(config):

    info_db = org.wayround.aipsetup.dbconnections.info_db(config)

    ret = info_ctl_new(config['info_repo']['dir'], info_db)

    return ret


def info_ctl_new(info_dir, info_db):

    ret = org.wayround.aipsetup.info.PackageInfoCtl(info_dir, info_db)

    return ret


def sys_ctl_by_config(config, info_ctl, pkg_repo_ctl, basedir='/'):

    ret = sys_ctl_new(
        info_ctl,
        pkg_repo_ctl,
        basedir,
        config['system_settings']['installed_pkg_dir'],
        config['system_settings']['installed_pkg_dir_buildlogs'],
        config['system_settings']['installed_pkg_dir_sums'],
        config['system_settings']['installed_pkg_dir_deps']
        )

    return ret


def sys_ctl_new(
    info_ctl,
    pkg_repo_ctl,
    basedir='/',
    installed_pkg_dir='/var/log/packages',
    installed_pkg_dir_buildlogs='/var/log/packages/buildlogs',
    installed_pkg_dir_sums='/var/log/packages/sums',
    installed_pkg_dir_deps='/var/log/packages/deps'
    ):

    ret = org.wayround.aipsetup.system.SystemCtl(
        info_ctl,
        pkg_repo_ctl,
        basedir,
        installed_pkg_dir,
        installed_pkg_dir_buildlogs,
        installed_pkg_dir_sums,
        installed_pkg_dir_deps
        )

    return ret


def bsite_ctl_new(path):

    ret = org.wayround.aipsetup.build.BuildingSiteCtl(path)

    return ret


def build_ctl_new(bs):

    ret = org.wayround.aipsetup.build.BuildCtl(bs)

    return ret


def pack_ctl_new(bs):

    ret = org.wayround.aipsetup.build.PackCtl(bs)

    return ret


def bscript_ctl_by_config(config):

    ret = bscript_ctl_new(
        config['builder_repo']['building_scripts_dir']
        )

    return ret


def bscript_ctl_new(dirname):

    ret = org.wayround.aipsetup.build.BuildScriptCtrl(
        dirname
        )

    return ret


def tag_ctl_by_config(config):

    tag_db = org.wayround.aipsetup.dbconnections.tag_db(config)

    ret = tag_ctl_new(
        config['info_repo']['tags_json'],
        tag_db
        )

    return ret


def tag_ctl_new(tags_json_filename_path, tag_db):

    ret = org.wayround.aipsetup.info.TagsControl(
        tag_db,
        tags_json_filename_path
        )

    return ret


def constitution_by_config(config, host, target, build):

    ret = None

    try:
        ret = org.wayround.aipsetup.build.Constitution(
            host_str=host,
            build_str=build,
            target_str=target
            )
    except org.wayround.utils.system_type.SystemTypeInvalidFullName:
        logging.error("Wrong host: {}".format(host))
        ret = 1
    else:

        ret.paths = dict(config['system_paths'])

    return ret


def asp_package(asp_filename):
    return org.wayround.aipsetup.package.ASPackage(asp_filename)

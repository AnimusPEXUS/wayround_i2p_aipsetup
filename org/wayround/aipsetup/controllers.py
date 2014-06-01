
import logging

import org.wayround.aipsetup.build
import org.wayround.aipsetup.client_pkg
import org.wayround.aipsetup.client_src
import org.wayround.aipsetup.dbconnections
import org.wayround.aipsetup.info
import org.wayround.aipsetup.package
import org.wayround.aipsetup.repository
import org.wayround.aipsetup.system
import org.wayround.utils.system_type


def pkg_repo_ctl_by_config(config):

    db_connection = org.wayround.aipsetup.dbconnections.pkg_repo_db(config)

    repository_dir = config['pkg_server']['repository_dir']
    garbage_dir = config['pkg_server']['garbage_dir']

    ret = pkg_repo_ctl_new(repository_dir, garbage_dir, db_connection)

    return ret


def pkg_repo_ctl_new(repository_dir, garbage_dir, pkg_repo_db):

    ret = org.wayround.aipsetup.repository.PackageRepoCtl(
        repository_dir, garbage_dir, pkg_repo_db
        )

    return ret


def src_repo_ctl_by_config(config):

    database_connection = \
        org.wayround.aipsetup.dbconnections.src_repo_db(config)

    sources_dir = config['src_server']['tarball_repository_root']

    ret = src_repo_ctl_new(sources_dir, database_connection)

    return ret


def src_repo_ctl_new(sources_dir, src_repo_db):

    ret = org.wayround.aipsetup.repository.SourceRepoCtl(
        sources_dir, src_repo_db
        )

    return ret


def src_paths_repo_ctl_by_config(config):

    database_connection = \
        org.wayround.aipsetup.dbconnections.src_paths_repo_db(config)

    sources_paths_json_filename = config['src_server']['src_paths_json']

    ret = src_paths_repo_ctl_new(
        sources_paths_json_filename,
        database_connection
        )

    return ret


def src_paths_repo_ctl_new(sources_paths_json_filename, src_paths_repo_db):

    ret = org.wayround.aipsetup.repository.SourcePathsRepoCtl(
        sources_paths_json_filename, src_paths_repo_db
        )

    return ret


def info_ctl_by_config(config):

    info_db = org.wayround.aipsetup.dbconnections.info_db(config)

    ret = info_ctl_new(config['pkg_server']['info_json_dir'], info_db)

    return ret


def info_ctl_new(info_dir, info_db):

    ret = org.wayround.aipsetup.info.PackageInfoCtl(info_dir, info_db)

    return ret


def sys_ctl_by_config(config, pkg_client, basedir='/'):

    ret = sys_ctl_new(
        pkg_client,
        basedir,
        config['system_settings']['installed_pkg_dir'],
        config['system_settings']['installed_pkg_dir_buildlogs'],
        config['system_settings']['installed_pkg_dir_sums'],
        config['system_settings']['installed_pkg_dir_deps']
        )

    return ret


def sys_ctl_new(
    pkg_client,
    basedir='/',
    installed_pkg_dir='/var/log/packages',
    installed_pkg_dir_buildlogs='/var/log/packages/buildlogs',
    installed_pkg_dir_sums='/var/log/packages/sums',
    installed_pkg_dir_deps='/var/log/packages/deps'
    ):

    ret = org.wayround.aipsetup.system.SystemCtl(
        pkg_client,
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
        config['local_build']['building_scripts_dir']
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
        config['pkg_server']['tags_json'],
        tag_db
        )

    return ret


def tag_ctl_new(tags_json_filename_path, tag_db):

    ret = org.wayround.aipsetup.info.TagsControl(
        tag_db,
        tags_json_filename_path
        )

    return ret


def bundles_ctl_by_config(config):
    return bundles_ctl_new(config['pkg_server']['bundles_dir'])


def bundles_ctl_new(dir_path):
    return org.wayround.aipsetup.info.BundlesCtl(dir_path)


def constitution_by_config(config, host, target, build):

    ret = None

    try:
        ret = org.wayround.aipsetup.build.Constitution(
            host_str=host,
            build_str=build,
            target_str=target
            )
    except org.wayround.utils.system_type.SystemTypeInvalidFullName:
        logging.exception("Wrong host: {}".format(host))
        ret = 1
    else:

        ret.paths = dict(config['system_paths'])

    return ret


def asp_package(asp_filename):
    return org.wayround.aipsetup.package.ASPackage(asp_filename)


def pkg_client_by_config(config):
    return pkg_client_new(
        config['pkg_client']['server_url'],
        config['pkg_client']['downloads_dir'],
        config['pkg_client']['acceptable_src_file_extensions']
        )


def pkg_client_new(
    url,
    downloads_dir='/tmp/aipsetup_downloads',
    acceptable_extensions_order_list=None
    ):
    return org.wayround.aipsetup.client_pkg.PackageServerClient(
        url,
        downloads_dir,
        acceptable_extensions_order_list
        )


def src_client_by_config(config):
    return src_client_new(config['src_client']['server_url'])


def src_client_new(url):
    return org.wayround.aipsetup.client_src.SourceServerClient(url)

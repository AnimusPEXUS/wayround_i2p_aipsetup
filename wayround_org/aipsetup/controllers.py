
import logging

import wayround_org.aipsetup.build
import wayround_org.aipsetup.client_pkg
import wayround_org.aipsetup.client_src
import wayround_org.aipsetup.dbconnections
import wayround_org.aipsetup.info
import wayround_org.aipsetup.package
import wayround_org.aipsetup.repository
import wayround_org.aipsetup.system
import wayround_org.utils.system_type


def pkg_repo_ctl_by_config(config):

    db_connection = wayround_org.aipsetup.dbconnections.pkg_repo_db(config)

    repository_dir = config['pkg_server']['repository_dir']
    garbage_dir = config['pkg_server']['garbage_dir']

    ret = pkg_repo_ctl_new(repository_dir, garbage_dir, db_connection)

    return ret


def pkg_repo_ctl_new(repository_dir, garbage_dir, pkg_repo_db):

    ret = wayround_org.aipsetup.repository.PackageRepoCtl(
        repository_dir, garbage_dir, pkg_repo_db
        )

    return ret


def src_repo_ctl_by_config(config):

    database_connection = \
        wayround_org.aipsetup.dbconnections.src_repo_db(config)

    sources_dir = config['src_server']['tarball_repository_root']

    ret = src_repo_ctl_new(sources_dir, database_connection)

    return ret


def src_repo_ctl_new(sources_dir, src_repo_db):

    ret = wayround_org.aipsetup.repository.SourceRepoCtl(
        sources_dir, src_repo_db
        )

    return ret


def info_ctl_by_config(config):

    info_db = wayround_org.aipsetup.dbconnections.info_db(config)

    ret = info_ctl_new(config['pkg_server']['info_json_dir'], info_db)

    return ret


def info_ctl_new(info_dir, info_db):

    ret = wayround_org.aipsetup.info.PackageInfoCtl(info_dir, info_db)

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

    ret = wayround_org.aipsetup.system.SystemCtl(
        pkg_client,
        basedir,
        installed_pkg_dir,
        installed_pkg_dir_buildlogs,
        installed_pkg_dir_sums,
        installed_pkg_dir_deps
        )

    return ret


def bsite_ctl_new(path):

    ret = wayround_org.aipsetup.build.BuildingSiteCtl(path)

    return ret


def build_ctl_new(bs):

    ret = wayround_org.aipsetup.build.BuildCtl(bs)

    return ret


def pack_ctl_new(bs):

    ret = wayround_org.aipsetup.build.PackCtl(bs)

    return ret


def bscript_ctl_by_config(config):

    ret = bscript_ctl_new(
        config['local_build']['building_scripts_dir']
        )

    return ret


def bscript_ctl_new(dirname):

    ret = wayround_org.aipsetup.build.BuildScriptCtrl(
        dirname
        )

    return ret


def tag_ctl_by_config(config):

    tag_db = wayround_org.aipsetup.dbconnections.tag_db(config)

    ret = tag_ctl_new(
        config['pkg_server']['tags_json'],
        tag_db
        )

    return ret


def tag_ctl_new(tags_json_filename_path, tag_db):

    ret = wayround_org.aipsetup.info.TagsControl(
        tag_db,
        tags_json_filename_path
        )

    return ret


def bundles_ctl_by_config(config):
    return bundles_ctl_new(config['pkg_server']['bundles_dir'])


def bundles_ctl_new(dir_path):
    return wayround_org.aipsetup.info.BundlesCtl(dir_path)


def constitution_by_config(config, host, target, build):

    ret = None

    try:
        ret = wayround_org.aipsetup.build.Constitution(
            host_str=host,
            build_str=build,
            target_str=target
            )
    except wayround_org.utils.system_type.SystemTypeInvalidFullName:
        logging.exception("Wrong host: {}".format(host))
        ret = 1
    else:

        ret.paths = dict(config['system_paths'])

    return ret


def asp_package(asp_filename):
    return wayround_org.aipsetup.package.ASPackage(asp_filename)


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
    return wayround_org.aipsetup.client_pkg.PackageServerClient(
        url,
        downloads_dir,
        acceptable_extensions_order_list
        )


def src_client_by_config(config):
    return src_client_new(config['src_client']['server_url'])


def src_client_new(url):
    return wayround_org.aipsetup.client_src.SourceServerClient(url)

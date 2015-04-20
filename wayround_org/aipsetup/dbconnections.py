
"""
Global aipsetup database connection facility

Allows minimize DB access requests
"""

import logging

import wayround_org.aipsetup.info
import wayround_org.aipsetup.repository


_info_db_connection = None
_pkg_repo_db_connection = None
_latest_db_connection = None
_tag_db_connection = None
_src_repo_db_connection = None
_src_paths_repo_db_connection = None


def info_db(config):
    """
    Returns info database connection creating it if needed
    """
    global _info_db_connection

    if not _info_db_connection:
        _info_db_connection = \
            info_db_new_connection(config['pkg_server']['info_db_config'])

    return _info_db_connection


def info_db_new_connection(config_string):
    """
    Returns info database connection creating it if needed
    """

    logging.info(
        "Getting info DB connection: {}".format(config_string)
        )
    ret = wayround_org.aipsetup.info.PackageInfo(
        config_string
        )

    ret.create_tables()

    return ret


def pkg_repo_db(config):
    """
    Returns package index database connection creating it if needed
    """

    global _pkg_repo_db_connection

    if not _pkg_repo_db_connection:
        _pkg_repo_db_connection = pkg_repo_db_new_connection(
            config['pkg_server']['repository_dir_index_db_config']
            )

    return _pkg_repo_db_connection


def pkg_repo_db_new_connection(config_string):
    """
    Returns package index database connection creating it if needed
    """

    logging.info(
        "Getting pkg repo DB connection: {}".format(
            config_string
            )
        )
    ret = wayround_org.aipsetup.repository.PackageRepo(
        config_string
        )

    ret.create_tables()

    return ret


def src_repo_db(config):
    """
    Returns sources database connection creating it if needed
    """

    global _src_repo_db_connection

    if not _src_repo_db_connection:
        _src_repo_db_connection = src_repo_db_new_connection(
            config['src_server']['src_index_db_config']
            )

    return _src_repo_db_connection


def src_repo_db_new_connection(config_string):
    """
    Returns sources database connection creating it if needed
    """
    logging.info(
        "Getting src repo DB connection: {}".format(
            config_string
            )
        )
    ret = wayround_org.aipsetup.repository.SourceRepo(
        config_string
        )

    ret.create_tables()

    return ret


def close_all():
    """
    Closes all open DB connections
    """
    # is words (only words not the meaning) 'global' can be removed here?
    global _info_db_connection
    global _pkg_repo_db_connection
    global _src_repo_db_connection

    # TODO: db classes shoud have no close() methods. remove garbage code.

    if _info_db_connection:
        if hasattr(_info_db_connection, 'close'):
            _info_db_connection.close()

    if _pkg_repo_db_connection:
        if hasattr(_pkg_repo_db_connection, 'close'):
            _pkg_repo_db_connection.close()

    if _src_repo_db_connection:
        if hasattr(_src_repo_db_connection, 'close'):
            _src_repo_db_connection.close()

    return

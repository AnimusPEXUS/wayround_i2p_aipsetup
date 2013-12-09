
"""
Global aipsetup database connection facility

Allows minimize DB access requests
"""

_info_db_connection = None
_pkg_repo_db_connection = None
_latest_db_connection = None
_tag_db_connection = None
_src_repo_db_connection = None


def info_db(config):
    """
    Returns info database connection creating it if needed
    """
    import org.wayround.aipsetup.info

    global _info_db_connection

    if not _info_db_connection:
        _info_db_connection = org.wayround.aipsetup.info.PackageInfo(
            config['info_repo']['index_db_config']
            )

    return _info_db_connection

def tag_db(config):
    """
    Returns tag database connection creating it if needed
    """
    import org.wayround.aipsetup.info

    global _tag_db_connection

    if not _tag_db_connection:
        _tag_db_connection = org.wayround.aipsetup.info.Tags(
            config['info_repo']['tags_db_config']
            )

    return _tag_db_connection

def pkg_repo_db(config):
    """
    Returns package index database connection creating it if needed
    """
    import org.wayround.aipsetup.repository

    global _pkg_repo_db_connection

    if not _pkg_repo_db_connection:
        _pkg_repo_db_connection = org.wayround.aipsetup.repository.PackageRepo(
            config['package_repo']['index_db_config']
            )

    return _pkg_repo_db_connection

def src_repo_db(config):
    """
    Returns sources database connection creating it if needed
    """
    import org.wayround.aipsetup.repository

    global _src_repo_db_connection

    if not _src_repo_db_connection:
        _src_repo_db_connection = org.wayround.aipsetup.repository.SourceRepo(
            config['sources_repo']['index_db_config']
            )

    return _src_repo_db_connection



def close_all():
    """
    Closes all open DB connections
    """
    global _info_db_connection
    global _pkg_repo_db_connection
    global _latest_db_connection
    global _tag_db_connection
    global _src_repo_db_connection

    if _info_db_connection:
        _info_db_connection.close()

    if _pkg_repo_db_connection:
        _pkg_repo_db_connection.close()

    if _latest_db_connection:
        _latest_db_connection.close()

    if _tag_db_connection:
        _tag_db_connection.close()

    if _src_repo_db_connection:
        _src_repo_db_connection.close()

    return

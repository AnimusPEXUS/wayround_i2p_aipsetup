
import org.wayround.aipsetup.pkgindex
import org.wayround.aipsetup.pkginfo
import org.wayround.aipsetup.pkglatest
import org.wayround.aipsetup.pkgtag

_info_db_connection = None
_index_db_connection = None
_latest_db_connection = None
_tag_db_connection = None
_src_db_connection = None

def info_db():

    global _info_db_connection

    if not _info_db_connection:
        _info_db_connection = org.wayround.aipsetup.pkginfo.PackageInfo()

    return _info_db_connection

def index_db():

    global _index_db_connection

    if not _index_db_connection:
        _index_db_connection = org.wayround.aipsetup.pkgindex.PackageIndex()

    return _index_db_connection

def latest_db():

    global _latest_db_connection

    if not _latest_db_connection:
        _latest_db_connection = org.wayround.aipsetup.pkglatest.PackageLatest()

    return _latest_db_connection

def tag_db():

    global _tag_db_connection

    if not _tag_db_connection:
        _tag_db_connection = org.wayround.aipsetup.pkgtag.package_tags_connection()

    return _tag_db_connection

def src_db():

    global _src_db_connection

    if not _src_db_connection:
        _src_db_connection = org.wayround.aipsetup.pkgindex.get_sources_connection()

    return _src_db_connection

def close_all():
    global _info_db_connection
    global _index_db_connection
    global _latest_db_connection
    global _tag_db_connection
    global _src_db_connection

    if _info_db_connection:
        _info_db_connection.close()

    if _index_db_connection:
        _index_db_connection.close()

    if _latest_db_connection:
        _latest_db_connection.close()

    if _tag_db_connection:
        _tag_db_connection.close()

    if _src_db_connection:
        _src_db_connection.close()


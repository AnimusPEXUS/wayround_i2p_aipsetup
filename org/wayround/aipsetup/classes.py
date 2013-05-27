
import org.wayround.aipsetup.dbconnections
import org.wayround.aipsetup.repository
import org.wayround.aipsetup.info
import org.wayround.aipsetup.package

def pkg_repo_ctl(config):

    repository_dir = config['package_repo']['dir']
    db_connection = org.wayround.aipsetup.dbconnections.pkg_repo_db(config)

    garbage_dir = config['package_repo']['garbage_dir']

    ret = org.wayround.aipsetup.repository.PackageRepoCtl(
        repository_dir, db_connection, garbage_dir
        )

    return ret

def src_repo_ctl(config):

    sources_dir = config['sources_repo']['dir']
    database_connection = org.wayround.aipsetup.dbconnections.src_repo_db(config)


    ret = org.wayround.aipsetup.repository.SourceRepoCtl(
        sources_dir, database_connection
        )

    return ret

def info_ctl(config):

    info_db = org.wayround.aipsetup.dbconnections.info_db(config)

    ret = org.wayround.aipsetup.info.PackageInfoCtl(
        info_dir=config['info_repo']['dir'],
        info_db=info_db
        )

    return ret

def sys_ctl(config, info_ctl, pkg_repo_ctl, basedir='/'):

    ret = org.wayround.aipsetup.system.SystemCtl(
        config, info_ctl, pkg_repo_ctl, basedir=basedir
        )

    return ret

def bsite_ctl(path):

    ret = org.wayround.aipsetup.build.BuildingSiteCtl(path)

    return ret

def build_ctl(bs):

    ret = org.wayround.aipsetup.build.BuildCtl(bs)

    return ret

def pack_ctl(bs):

    ret = org.wayround.aipsetup.build.PackCtl(bs)

    return ret

def bscript_ctl(config):

    ret = org.wayround.aipsetup.build.BuildScriptCtrl(
        config['builder_repo']['building_scripts_dir']
        )

    return ret

def tag_ctl(config):

    tag_db = org.wayround.aipsetup.dbconnections.tag_db(config)

    ret = org.wayround.aipsetup.info.TagsControl(
        tag_db,
        config['info_repo']['tags_json']
        )

    return ret

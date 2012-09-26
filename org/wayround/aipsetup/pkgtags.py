
import org.wayround.utils.tag

import org.wayround.aipsetup.config

def pkgtags_tag_editor(opts, args):

    ret = 0

    tag_editor(None, None)

    return ret


def package_tags_connection():
    return org.wayround.utils.tag.TagEngine(
        org.wayround.aipsetup.config.config['package_tags_db_config']
        )

def tag_editor(mode, name):
    import org.wayround.aipsetup.tageditor

    ret = org.wayround.aipsetup.tageditor.main(mode, name)

    return ret


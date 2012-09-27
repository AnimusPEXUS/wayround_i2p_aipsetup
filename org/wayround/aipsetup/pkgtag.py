
import os.path
import logging
import json

import org.wayround.utils.tag
import org.wayround.utils.file

import org.wayround.aipsetup.config
import org.wayround.aipsetup.info



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

def load_tags_from_fs(tag_db=None):

    if tag_db == None:
        raise ValueError("tag_db can't be None")


    file_name = org.wayround.aipsetup.config.config['tags']

    try:
        f = open(file_name, 'r')
    except:
        logging.exception("Couldn't open file `{}'".format(file_name))
    else:
        try:
            txt = f.read()

            d = json.loads(txt)

            tag_db.clear()

            keys = list(d.keys())
            keys.sort()

            count = len(keys)
            num = 0
            for i in keys:
                num += 1

                if num == 0:
                    perc = 0
                else:
                    perc = float(100) / (float(count) / float(num))
                org.wayround.utils.file.progress_write('    {:6.2f}%'.format(perc))
                tag_db.set_tags(i, d[i])

            org.wayround.utils.file.progress_write_finish()
        finally:

            f.close()

    return

def save_tags_to_fs(tag_db=None):

    if tag_db == None:
        raise ValueError("tag_db can't be None")

    file_name = org.wayround.aipsetup.config.config['tags']

    logging.info("Getting tags from DB")

    d = tag_db.get_objects_and_tags_dict()

    logging.info("Creating JSON object")

    txt = json.dumps(d, sort_keys=True, indent=2)

    logging.info("Saving to file `{}'".format(file_name))
    try:
        f = open(file_name, 'w')
    except:
        logging.exception("Couldn't create file `{}'".format(file_name))
    else:
        try:
            f.write(txt)
        except:
            raise
        else:
            logging.info("Saved")
        finally:

            f.close()

    return

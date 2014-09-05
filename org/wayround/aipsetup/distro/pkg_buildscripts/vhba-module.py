
import os.path
import logging
import subprocess

import org.wayround.utils.file

import org.wayround.aipsetup.build
import org.wayround.aipsetup.buildtools.autotools as autotools


def main(buildingsite, action=None):

    ret = 0

    r = org.wayround.aipsetup.build.build_script_wrap(
        buildingsite,
        ['extract', 'patch', 'build', 'distribute', 'afterdist'],
        action,
        "help"
        )

    if not isinstance(r, tuple):
        logging.error("Error")
        ret = r

    else:

        pkg_info, actions = r

        src_dir = org.wayround.aipsetup.build.getDIR_SOURCE(buildingsite)

        dst_dir = org.wayround.aipsetup.build.getDIR_DESTDIR(buildingsite)

        separate_build_dir = False

        source_configure_reldir = '.'

        p = subprocess.Popen(['uname', '-r'], stdout=subprocess.PIPE)
        text = p.communicate()
        p.wait()
        kern_rel = str(text[0].splitlines()[0], encoding='utf-8')

        logging.info("`uname -r' returned: {}".format(repr(kern_rel)))

        kdir = os.path.join(
            dst_dir,
            'lib',
            'modules',
            kern_rel
            )
#
#        try:
#            os.makedirs(kdir, mode=0o700)
#        except:
#            logging.error("Can't create dir {}".format(kdir))

        if 'extract' in actions:
            if os.path.isdir(src_dir):
                logging.info("cleaningup source dir")
                org.wayround.utils.file.cleanup_dir(src_dir)
            ret = autotools.extract_high(
                buildingsite,
                pkg_info['pkg_info']['basename'],
                unwrap_dir=True,
                rename_dir=False
                )

        if 'patch' in actions and ret == 0:

            try:
                makefile = open(src_dir + os.path.sep + 'Makefile', 'r')
                lines = makefile.readlines()
                makefile.close()

                for each in range(len(lines)):
                    if lines[each] == '\t$(MAKE) -C $(KDIR) M=$(PWD) $@\n':
                        lines[each] = '\t$(MAKE) -C $(KDIR) M=$(PWD) INSTALL_MOD_PATH=$(DESTDIR) $@\n'

                makefile = open(src_dir + os.path.sep + 'Makefile', 'w')
                makefile.writelines(lines)
                makefile.close()
            except:
                logging.exception("Error. See exception message")
                ret = 10

        if 'build' in actions and ret == 0:
            logging.info("Working in `{}'".format(src_dir))
            ret = autotools.make_high(
                buildingsite,
                options=[],
                arguments=[
                    'PWD=' + src_dir,
                    'KERNELRELEASE=' + kern_rel,
                    'DESTDIR=' + dst_dir
                    ],
                environment={},
                environment_mode='copy',
                use_separate_buildding_dir=separate_build_dir,
                source_configure_reldir=source_configure_reldir
                )

        if 'distribute' in actions and ret == 0:
            logging.info("Working in `{}'".format(src_dir))
            ret = autotools.make_high(
                buildingsite,
                options=[],
                arguments=[
                    'install',
                    'PWD=' + src_dir,
                    'KERNELRELEASE=' + kern_rel,
                    'DESTDIR=' + dst_dir
                    ],
                environment={},
                environment_mode='copy',
                use_separate_buildding_dir=separate_build_dir,
                source_configure_reldir=source_configure_reldir
                )

        if 'afterdist' in actions and ret == 0:

            try:
                files = os.listdir(kdir)

                for i in files:
                    fname = os.path.join(kdir, i)
                    if os.path.isfile(fname):
                        os.unlink(fname)

            except:
                logging.exception("Error. See exception message")
                ret = 11

    return ret
